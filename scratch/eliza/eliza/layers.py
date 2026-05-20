"""Eliza.Layers — brick adaptations of existing modules.

Each Layer wraps one production module as a Brick conforming to the
protocol. The DBE analysis collapsed Phase B (slices 5-12) into one
extraction template applied 8 times; this module is the result.

Each Layer:
  * Holds the wrapped state as an attribute.
  * Implements `step(d_in, s_in) -> (d_out, s_out)` per the Brick protocol.
  * Exposes `brick_type`, `witnesses`, `homomorphism_tag`, `name`.
  * Emits `stats()` returning a dict slice for `compression_stats`.

The wrapped state remains MUTABLE on the Layer instance so that the
existing modules' update-in-place semantics is preserved. The
brick.step() returns `(d_out, layer)` where the same layer instance is
passed through; downstream code can ignore the S edge or use it for
threading discipline.

The 8 Extract instances (one per row in the DBE trace):
  * ChamberLayer        — router + manifold + cocycle + holonomy
  * PredictorLayer      — TrigramPredictor
  * SequiturCharLayer   — grammar_char + gt_trigram_update
  * SequiturOrbitLayer  — grammar_orbit
  * GeoSppfLayer        — geo_sequitur
  * CoalgLayer          — coalgebraic codec
  * RecorderTee         — SessionRecorder (as Tee, not a regular layer)
  * StepResultAggregator — bundles into StepResult (handled in pipeline)
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, Optional, Tuple

from eliza.alphabets import Chamber
from eliza.brick import BrickType, Unit, UNIT, Witnessing
from eliza.coalgebraic import CoalgebraicCodec
from eliza.geo_sequitur import GeometricSPPF
from eliza.holonomy import Holonomy, HolonomyReading
from eliza.manifold import Manifold, word_str
from eliza.orbit import Cocycle, OrbitInfo
from eliza.predictor import TrigramPredictor
from eliza.router import Router, default as default_router
from eliza.sequitur import Sequitur
from eliza.trajectory import detect_period


TRAJECTORY_WINDOW = 24


# --- ChamberLayer ----------------------------------------------------------


@dataclass
class ChamberState:
    """The state held by ChamberLayer (Chamber walk + trajectory)."""
    chamber: Chamber
    trajectory: Deque[Chamber]


@dataclass
class ChamberObservation:
    """The D-out of ChamberLayer: per-step chamber/orbit/holonomy readout."""
    char: str
    chamber_from: Chamber
    chamber_to: Chamber
    chamber_from_word: str
    chamber_to_word: str
    orbit: OrbitInfo
    holonomy: HolonomyReading
    period: Optional[int]


@dataclass
class ChamberLayer:
    """Router → manifold.apply → cocycle.info → holonomy.at, as a brick.

    Witnessing: C⇒S (the per-step compute mutates the chamber/trajectory
    state; the data char witnesses the mutation).
    """
    manifold: Manifold
    cocycle: Cocycle
    holonomy: Holonomy
    router: Router
    state: ChamberState = field(init=False)
    name: str = "chamber"
    homomorphism_tag: str = "S₄ right-equivariance"

    def __post_init__(self):
        self.state = ChamberState(
            chamber=self.manifold.origin(),
            trajectory=deque([self.manifold.origin()], maxlen=TRAJECTORY_WINDOW),
        )

    @property
    def brick_type(self) -> BrickType:
        return BrickType(
            D_in=str, D_out=ChamberObservation, S_in=ChamberState, S_out=ChamberState
        )

    @property
    def witnesses(self) -> Witnessing:
        return Witnessing.C_TO_S

    def step(self, ch: str, _: Any = None) -> Tuple[ChamberObservation, ChamberState]:
        from_chamber = self.state.chamber
        from_word = word_str(self.manifold.shortlex_word(from_chamber))
        gen_or_perm = self.router(ch)
        if isinstance(gen_or_perm, tuple):
            from eliza.alphabets import perm_compose
            new_chamber = perm_compose(from_chamber, gen_or_perm)
        else:
            from eliza.manifold import apply as _apply
            new_chamber = _apply(gen_or_perm, from_chamber)
        self.state.chamber = new_chamber
        self.state.trajectory.append(new_chamber)
        to_word = word_str(self.manifold.shortlex_word(new_chamber))
        info = self.cocycle.info(new_chamber)
        holonomy = self.holonomy.at(new_chamber)
        period = detect_period(list(self.state.trajectory))
        obs = ChamberObservation(
            char=ch, chamber_from=from_chamber, chamber_to=new_chamber,
            chamber_from_word=from_word, chamber_to_word=to_word,
            orbit=info, holonomy=holonomy, period=period,
        )
        return obs, self.state

    def stats(self) -> Dict[str, Any]:
        # Chamber layer doesn't contribute compression numbers itself.
        return {}


# --- PredictorLayer --------------------------------------------------------


@dataclass
class PredictorLayer:
    """Wraps TrigramPredictor.surprise + .update.

    The brick's D-in is the char; D-out is the surprise (Optional[float]);
    S is the predictor itself. Witnessing: C⇒S (update); the surprise
    is read BEFORE the update (S⇒D side) and emitted on D-out.

    For pipeline composition, this layer combines BOTH the read (surprise)
    and the write (update) into one step. The surprise reflects the
    state BEFORE the update.
    """
    predictor: TrigramPredictor
    _n_obs: int = 0
    _cum_surprise_bits: float = 0.0
    name: str = "predictor"
    homomorphism_tag: str = "Markov-3 free commutative monoid"

    @property
    def brick_type(self) -> BrickType:
        return BrickType(
            D_in=str, D_out=type(None), S_in=TrigramPredictor, S_out=TrigramPredictor
        )

    @property
    def witnesses(self) -> Witnessing:
        return Witnessing.C_TO_S

    def step(self, ch: str, _: Any = None) -> Tuple[Optional[float], TrigramPredictor]:
        surprise = self.predictor.surprise_bits(ch)
        if surprise is not None:
            self._n_obs += 1
            self._cum_surprise_bits += surprise
        self.predictor.update(ch)
        return surprise, self.predictor

    def stats(self) -> Dict[str, Any]:
        import math
        if self._n_obs == 0:
            return {
                "symbols": 0,
                "bits_per_symbol": 0.0,
                "compressed_bits": 0.0,
                "ratio": float("inf"),
            }
        bps = self._cum_surprise_bits / self._n_obs
        raw_bits = math.log2(self.predictor.vocab_size) if self.predictor.vocab_size > 1 else 1.0
        return {
            "symbols": self._n_obs,
            "raw_bits_per_symbol": raw_bits,
            "bits_per_symbol": bps,
            "compressed_bits": self._cum_surprise_bits,
            "ratio": raw_bits / bps if bps > 0 else float("inf"),
        }


# --- SequiturCharLayer + SequiturOrbitLayer -------------------------------


@dataclass
class SequiturLayer:
    """Wraps a Sequitur grammar instance. Stateless wrt the input D;
    the grammar mutates on each observation.

    Used twice: once for char (`SequiturCharLayer`) and once for orbit
    (`SequiturOrbitLayer`). The grammar is the S; the input symbol is
    the D. Witnessing: C⇒S.
    """
    grammar: Sequitur
    name: str = "sequitur"
    homomorphism_tag: str = "digram-uniqueness + rule-utility invariants"

    @property
    def brick_type(self) -> BrickType:
        return BrickType(
            D_in=object, D_out=type(None), S_in=Sequitur, S_out=Sequitur
        )

    @property
    def witnesses(self) -> Witnessing:
        return Witnessing.C_TO_S

    def step(self, sym: Any, _: Any = None) -> Tuple[None, Sequitur]:
        self.grammar.observe(sym)
        return None, self.grammar

    def stats(self) -> Dict[str, Any]:
        return {f"{self.name}_n_rules": self.grammar.n_rules()}


def SequiturCharLayer(grammar: Sequitur) -> SequiturLayer:
    return SequiturLayer(grammar=grammar, name="grammar_char",
                         homomorphism_tag="digram-uniqueness (char alphabet)")


def SequiturOrbitLayer(grammar: Sequitur) -> SequiturLayer:
    return SequiturLayer(grammar=grammar, name="grammar_orbit",
                         homomorphism_tag="digram-uniqueness (S₃ alphabet)")


# --- GeoSppfLayer ---------------------------------------------------------


@dataclass
class GeoSppfLayer:
    """Wraps GeometricSPPF as a brick."""
    sppf: GeometricSPPF
    name: str = "geo_sppf"
    homomorphism_tag: str = "WH-cell partition (Klein-quotient)"

    @property
    def brick_type(self) -> BrickType:
        return BrickType(
            D_in=str, D_out=type(None), S_in=GeometricSPPF, S_out=GeometricSPPF
        )

    @property
    def witnesses(self) -> Witnessing:
        return Witnessing.C_TO_S

    def step(self, ch: str, _: Any = None) -> Tuple[None, GeometricSPPF]:
        self.sppf.observe(ch)
        return None, self.sppf

    def stats(self) -> Dict[str, Any]:
        return {
            "geo_total_bits": self.sppf.compression_bits(),
            "geo_n_rules": self.sppf.n_rules(),
            "geo_cell_population": self.sppf.cell_population(),
        }


# --- CoalgLayer ----------------------------------------------------------


@dataclass
class CoalgLayer:
    """Wraps CoalgebraicCodec as a brick.

    D-in: Chamber (the post-walk chamber).
    D-out: the slot just emitted (V₄ label).
    S: CoalgebraicCodec.
    Witnessing: C⇒S (the slot is also exposed on D-out as a Tap).
    """
    codec: CoalgebraicCodec
    name: str = "coalg"
    homomorphism_tag: str = "coalgebra: unfold = predict"

    @property
    def brick_type(self) -> BrickType:
        return BrickType(
            D_in=tuple, D_out=float, S_in=CoalgebraicCodec, S_out=CoalgebraicCodec
        )

    @property
    def witnesses(self) -> Witnessing:
        return Witnessing.C_TO_S

    def step(self, chamber: Chamber, _: Any = None) -> Tuple[float, CoalgebraicCodec]:
        bits = self.codec.step(chamber)
        return bits, self.codec

    def stats(self) -> Dict[str, Any]:
        import math
        bps = (
            self.codec.compression_bits() / self.codec.n_steps()
            if self.codec.n_steps() > 0 else 2.0
        )
        coalg_raw_bits = 2.0
        return {
            "coalg_total_bits": self.codec.compression_bits(),
            "coalg_bits_per_slot": bps,
            "coalg_raw_bits_per_slot": coalg_raw_bits,
            "coalg_slot_ratio": (
                coalg_raw_bits / bps if bps > 0 else float("inf")
            ),
            "coalg_n_contexts": self.codec.n_contexts(),
        }


# --- RecorderTee (slice 1) -------------------------------------------------

from eliza.recorder import SessionRecorder, Turn


@dataclass
class RecorderTee:
    """Tee around ChamberLayer: persist per-step facts to SQLite as a
    side-channel. The chamber observation passes through unchanged; the
    recorder writes externally.

    Conceptually a `Tee(ChamberLayer, observer=persist_turn)`. This
    impl bundles the inner layer and observer into one brick for
    convenience.
    """
    inner: ChamberLayer
    recorder: SessionRecorder
    predictor: TrigramPredictor   # needed to read (c1, c2) for trigram persistence
    _n: int = 0
    name: str = "recorder_tee"
    homomorphism_tag: str = "comonadic observation"

    @property
    def brick_type(self) -> BrickType:
        return self.inner.brick_type

    @property
    def witnesses(self) -> Witnessing:
        return self.inner.witnesses

    def step(self, ch: str, _: Any = None) -> Tuple[ChamberObservation, ChamberState]:
        # Read (c1, c2) BEFORE the inner step (the recorder needs the
        # pre-update predictor context to align with the inline Engine).
        c1, c2 = self.predictor.context
        obs, state = self.inner.step(ch, self.inner.state)
        if self.recorder is not None:
            self.recorder.record_turn(
                Turn(
                    n=0,  # SessionRecorder fills in monotonically
                    user_input=ch,
                    generator=self.inner.router(ch) if not isinstance(self.inner.router(ch), tuple) else None,
                    chamber_from=obs.chamber_from_word,
                    chamber_to=obs.chamber_to_word,
                    bruhat=self.inner.manifold.bruhat_distance(obs.chamber_to),
                    fiedler=self.inner.manifold.fiedler_value(obs.chamber_to),
                    turbulence=self.inner.manifold.turbulence_value(obs.chamber_to),
                    holonomy_closes=obs.holonomy.closes,
                    holonomy_target=word_str(
                        self.inner.manifold.shortlex_word(obs.holonomy.target)
                    ),
                    curvature=obs.holonomy.curvature,
                    curvature_band=obs.holonomy.band,
                    surprise=None,  # surprise tracked by PredictorLayer
                )
            )
            if c1 and c2:
                self.recorder.record_trigram(c1, c2, ch)
        return obs, state

    def stats(self) -> Dict[str, Any]:
        return self.inner.stats()


# --- GtTrigramLayer + HuffmanLayer + GrammarStatsLayer (slice 2) -----------


import math
from typing import Optional as _Optional
from eliza.alphabets import ORIGIN, V4_LABELS
from eliza.sequitur import NT as _NT


@dataclass
class GtTrigramLayer:
    """Grammar-trigram update + the 4-way cost suite (gt, gt6, gtV4a/d).

    Mirrors Engine._update_grammar_trigram + _grammar_trigram_cost_of_top
    + _gt_costs_of_top. Holds the four count tables and the emission
    counter; exposes the costs as stats.

    Witnessing: C⇒S (per-step update); stats() is the S⇒D read.
    """
    cocycle: Cocycle
    grammar_char: Sequitur  # shared with SequiturCharLayer
    predictor: TrigramPredictor  # for vocab_size during cost calcs
    router: Router
    manifold: Manifold

    # State.
    _gt_context: Tuple[Any, Any] = field(default=(None, None))
    _gt_counts: Dict[Tuple[Any, Any], Dict[Any, int]] = field(default_factory=dict)
    _gt6_counts: Dict[Tuple[Any, Any, str], Dict[Any, int]] = field(default_factory=dict)
    _gtV4a_counts: Dict[Tuple[Any, Any, str], Dict[Any, int]] = field(default_factory=dict)
    _gtV4d_counts: Dict[Tuple[Any, Any, str], Dict[Any, int]] = field(default_factory=dict)
    _orbit_emit_counts: Dict[str, Dict[Any, int]] = field(default_factory=dict)
    _emission_count: int = 0
    _tetrad_frame_orbit: str = "e"
    _gt_cum_surprise: float = 0.0
    name: str = "gt_trigram"
    homomorphism_tag: str = "DirectProduct(free monoid, S₃ residue)"

    @property
    def brick_type(self) -> BrickType:
        return BrickType(D_in=object, D_out=type(None), S_in=dict, S_out=dict)

    @property
    def witnesses(self) -> Witnessing:
        return Witnessing.C_TO_S

    def step(self, current_chamber: Chamber, _: Any = None) -> Tuple[None, Any]:
        """Per-step update — call AFTER grammar_char.observe(ch) and after
        the chamber walk has updated current_chamber."""
        top = self.grammar_char.top_rule()
        if not top:
            return None, self
        emit_raw = top[-1]
        emit = emit_raw
        c1, c2 = self._gt_context
        orbit = self.cocycle.orbit_of(current_chamber)
        if c1 is not None and c2 is not None:
            inner = self._gt_counts.get((c1, c2), {})
            total = sum(inner.values())
            vocab = self.predictor.vocab_size + self.grammar_char.n_rules()
            p = (inner.get(emit, 0) + 0.5) / (total + 0.5 * vocab)
            surprise = -math.log2(p) if p > 0 else 32.0
            self._gt_cum_surprise += surprise
            self._gt_counts.setdefault((c1, c2), {})
            self._gt_counts[(c1, c2)][emit] = self._gt_counts[(c1, c2)].get(emit, 0) + 1
            self._gt6_counts.setdefault((c1, c2, orbit), {})
            self._gt6_counts[(c1, c2, orbit)][emit_raw] = (
                self._gt6_counts[(c1, c2, orbit)].get(emit_raw, 0) + 1
            )
            pos_in_tetrad = self._emission_count % 4
            if pos_in_tetrad == 0:
                self._tetrad_frame_orbit = orbit
            v4_canonical = V4_LABELS[pos_in_tetrad]
            slot_abs = self.cocycle.s3_on_v4(orbit, v4_canonical)
            self._gtV4a_counts.setdefault((c1, c2, slot_abs), {})
            self._gtV4a_counts[(c1, c2, slot_abs)][emit_raw] = (
                self._gtV4a_counts[(c1, c2, slot_abs)].get(emit_raw, 0) + 1
            )
            relative = self.cocycle.relative_orbit(orbit, self._tetrad_frame_orbit)
            slot_dlt = self.cocycle.s3_on_v4(relative, v4_canonical)
            self._gtV4d_counts.setdefault((c1, c2, slot_dlt), {})
            self._gtV4d_counts[(c1, c2, slot_dlt)][emit_raw] = (
                self._gtV4d_counts[(c1, c2, slot_dlt)].get(emit_raw, 0) + 1
            )
        self._gt_context = (c2, emit_raw)
        self._emission_count += 1
        bucket = self._orbit_emit_counts.setdefault(orbit, {})
        bucket[emit_raw] = bucket.get(emit_raw, 0) + 1
        return None, self

    def _walk_symbol_for_top(self, sym, start) -> Tuple[Chamber, int]:
        from eliza.manifold import apply as _apply
        from eliza.alphabets import perm_compose
        if isinstance(sym, _NT):
            rule = self.grammar_char.rules.get(sym.rule_id)
            if rule is None:
                return start, 0
            chamber = start
            total = 0
            for node in rule.body_iter():
                chamber, n = self._walk_symbol_for_top(node.sym, chamber)
                total += n
            return chamber, total
        action = self.router(sym) if isinstance(sym, str) and len(sym) == 1 else None
        if action is None:
            return start, 0
        if isinstance(action, tuple):
            return perm_compose(start, action), 1
        return _apply(action, start), 1

    def _gt_costs(self) -> Tuple[float, float, float, float, float]:
        """Returns (gt_cost, gt6_cost, gtV4a_cost, gtV4d_cost, cycling_rate).
        Mirror of Engine._gt_costs_of_top + _grammar_trigram_cost_of_top."""
        top = self.grammar_char.top_rule()
        if len(top) < 3:
            return 0.0, 0.0, 0.0, 0.0, 0.0
        gt_cost = 0.0
        gt6_cost = 0.0
        gtV4a_cost = 0.0
        gtV4d_cost = 0.0
        vocab = self.predictor.vocab_size + self.grammar_char.n_rules()
        chamber = ORIGIN
        chambers_at: list = [ORIGIN]
        powers: list = []
        for sym in top:
            new_chamber, n_steps = self._walk_symbol_for_top(sym, chamber)
            chamber = new_chamber
            chambers_at.append(chamber)
            powers.append(n_steps)
        for i in range(2, len(top)):
            orbit = self.cocycle.orbit_of(chambers_at[i])
            emit = top[i]
            # gt cost (plain)
            inner = self._gt_counts.get((top[i - 2], top[i - 1]), {})
            total = sum(inner.values())
            p = (inner.get(emit, 0) + 0.5) / (total + 0.5 * vocab)
            gt_cost += -math.log2(p) if p > 0 else 32.0
            # gt6 cost
            pos_in_tetrad = i % 4
            v4_canonical = V4_LABELS[pos_in_tetrad]
            tetrad_start = i - pos_in_tetrad
            frame_orbit = self.cocycle.orbit_of(chambers_at[tetrad_start])
            slot_abs = self.cocycle.s3_on_v4(orbit, v4_canonical)
            slot_dlt = self.cocycle.s3_on_v4(
                self.cocycle.relative_orbit(orbit, frame_orbit),
                v4_canonical,
            )
            inner = self._gt6_counts.get((top[i - 2], top[i - 1], orbit), {})
            total = sum(inner.values())
            p = (inner.get(emit, 0) + 0.5) / (total + 0.5 * vocab)
            gt6_cost += -math.log2(p) if p > 0 else 32.0
            inner = self._gtV4a_counts.get((top[i - 2], top[i - 1], slot_abs), {})
            total = sum(inner.values())
            p = (inner.get(emit, 0) + 0.5) / (total + 0.5 * vocab)
            gtV4a_cost += -math.log2(p) if p > 0 else 32.0
            inner = self._gtV4d_counts.get((top[i - 2], top[i - 1], slot_dlt), {})
            total = sum(inner.values())
            p = (inner.get(emit, 0) + 0.5) / (total + 0.5 * vocab)
            gtV4d_cost += -math.log2(p) if p > 0 else 32.0
        # Cycling rate.
        weighted_transitions = 0
        total_weight = 0
        prev = self.cocycle.orbit_of(chambers_at[1])
        for i in range(2, len(chambers_at)):
            cur = self.cocycle.orbit_of(chambers_at[i])
            w = powers[i - 1]
            total_weight += w
            if cur != prev:
                weighted_transitions += w
            prev = cur
        rate = weighted_transitions / total_weight if total_weight > 0 else 0.0
        return gt_cost, gt6_cost, gtV4a_cost, gtV4d_cost, rate

    def stats(self) -> Dict[str, Any]:
        n_obs = self._emission_count
        raw_bits = math.log2(self.predictor.vocab_size) if self.predictor.vocab_size > 1 else 1.0
        gt_cost, gt6_cost, gtV4a_cost, gtV4d_cost, rate = self._gt_costs()
        out = {}
        out["gt_total_bits"] = gt_cost
        out["gt_bits_per_symbol"] = gt_cost / n_obs if n_obs > 0 else raw_bits
        out["gt_ratio"] = (
            raw_bits / out["gt_bits_per_symbol"] if out["gt_bits_per_symbol"] > 0 else float("inf")
        )
        out["gt6_total_bits"] = gt6_cost
        out["gt6_bits_per_symbol"] = gt6_cost / n_obs if n_obs > 0 else raw_bits
        out["gt6_ratio"] = (
            raw_bits / out["gt6_bits_per_symbol"] if out["gt6_bits_per_symbol"] > 0 else float("inf")
        )
        out["gtV4a_total_bits"] = gtV4a_cost
        out["gtV4a_bits_per_symbol"] = gtV4a_cost / n_obs if n_obs > 0 else raw_bits
        out["gtV4a_ratio"] = (
            raw_bits / out["gtV4a_bits_per_symbol"] if out["gtV4a_bits_per_symbol"] > 0 else float("inf")
        )
        out["gtV4d_total_bits"] = gtV4d_cost
        out["gtV4d_bits_per_symbol"] = gtV4d_cost / n_obs if n_obs > 0 else raw_bits
        out["gtV4d_ratio"] = (
            raw_bits / out["gtV4d_bits_per_symbol"] if out["gtV4d_bits_per_symbol"] > 0 else float("inf")
        )
        out["orbit_cycling_rate"] = rate
        return out


@dataclass
class HuffmanLayer:
    """Read-only stats for Huffman code-length bits over the SPPF."""
    grammar_char: Sequitur
    predictor: TrigramPredictor
    gt_layer: GtTrigramLayer  # for orbit_emit_counts
    name: str = "huffman"
    homomorphism_tag: str = "Huffman code over SPPF"

    @property
    def brick_type(self) -> BrickType:
        return BrickType(D_in=type(None), D_out=dict, S_in=Sequitur, S_out=Sequitur)

    @property
    def witnesses(self) -> Witnessing:
        return Witnessing.S_TO_D

    def step(self, d_in: Any, s_in: Any) -> Tuple[dict, Sequitur]:
        return self.stats(), self.grammar_char

    @staticmethod
    def _huffman_code_lengths(counts: Dict[Any, int]) -> Dict[Any, int]:
        import heapq
        if not counts:
            return {}
        if len(counts) == 1:
            return {next(iter(counts)): 1}
        heap = []
        for i, (sym, count) in enumerate(counts.items()):
            heapq.heappush(heap, (count, i, [sym]))
        next_i = len(counts)
        while len(heap) > 1:
            c1, _, s1 = heapq.heappop(heap)
            c2, _, s2 = heapq.heappop(heap)
            heapq.heappush(heap, (c1 + c2, next_i, s1 + s2))
            next_i += 1
        _, _, all_syms = heap[0]
        # Re-derive code lengths via tree walk.
        # Simpler: compute via repeated merging tracked separately.
        # Use the recursive method.
        return _huffman_lengths_via_merge(counts)

    def _huffman_grammar_bits(self) -> float:
        """Total bits for the grammar under marginal Huffman."""
        # Collect all SPPF symbol occurrences.
        from collections import Counter
        counter: Dict[Any, int] = Counter()
        for rule in self.grammar_char.rules.values():
            for node in rule.body_iter():
                counter[node.sym] += 1
        lengths = _huffman_lengths_via_merge(counter)
        return float(sum(lengths.get(sym, 0) * cnt for sym, cnt in counter.items()))

    def _orbit_huffman_bits(self) -> Tuple[float, Dict[str, float]]:
        total_bits = 0.0
        per_orbit: Dict[str, float] = {}
        for orbit, emit_counts in self.gt_layer._orbit_emit_counts.items():
            lengths = _huffman_lengths_via_merge(emit_counts)
            orbit_bits = sum(
                lengths.get(sym, 0) * cnt for sym, cnt in emit_counts.items()
            )
            per_orbit[orbit] = float(orbit_bits)
            total_bits += orbit_bits
        return float(total_bits), per_orbit

    def stats(self) -> Dict[str, Any]:
        n_obs = self.gt_layer._emission_count
        raw_bits = math.log2(self.predictor.vocab_size) if self.predictor.vocab_size > 1 else 1.0
        huffman_bits = self._huffman_grammar_bits()
        orbit_huffman_bits, per_orbit = self._orbit_huffman_bits()
        bps_h = huffman_bits / n_obs if n_obs > 0 else raw_bits
        bps_oh = orbit_huffman_bits / n_obs if n_obs > 0 else raw_bits
        return {
            "huffman_total_bits": huffman_bits,
            "huffman_bits_per_symbol": bps_h,
            "huffman_ratio": raw_bits / bps_h if bps_h > 0 else float("inf"),
            "orbit_huffman_total_bits": orbit_huffman_bits,
            "orbit_huffman_bits_per_symbol": bps_oh,
            "orbit_huffman_ratio": raw_bits / bps_oh if bps_oh > 0 else float("inf"),
            "orbit_huffman_per_orbit": per_orbit,
        }


def _huffman_lengths_via_merge(counts: Dict[Any, int]) -> Dict[Any, int]:
    """Huffman code lengths via greedy merging; same as Engine's
    _huffman_code_lengths."""
    import heapq
    if not counts:
        return {}
    if len(counts) == 1:
        return {next(iter(counts)): 1}
    # Each heap entry: (weight, tiebreak, leaves)
    # Track depth per leaf via incremental merging.
    leaves = list(counts.items())
    lengths: Dict[Any, int] = {sym: 0 for sym, _ in leaves}
    heap = [(w, i, [s]) for i, (s, w) in enumerate(leaves)]
    heapq.heapify(heap)
    next_i = len(leaves)
    while len(heap) > 1:
        w1, _, syms1 = heapq.heappop(heap)
        w2, _, syms2 = heapq.heappop(heap)
        for s in syms1:
            lengths[s] += 1
        for s in syms2:
            lengths[s] += 1
        heapq.heappush(heap, (w1 + w2, next_i, syms1 + syms2))
        next_i += 1
    return lengths
