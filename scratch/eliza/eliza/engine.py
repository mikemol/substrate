"""Eliza.Engine — n-ary composition of all layers.

Per the Agda contract: per-char `step(ch)` threads through Router →
Manifold → Orbit → Holonomy → Predictor → Sequitur grammars → Recorder.
No layer reaches into another's internals; everything goes through
published methods.

The Engine is the SOLE assembly point. Outside the Engine, modules
are independent and reusable.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Deque, Dict, Optional, Tuple

from eliza.alphabets import Chamber
from eliza.holonomy import Holonomy, HolonomyReading
from eliza.manifold import Manifold, word_str
from eliza.orbit import Cocycle
from eliza.predictor import TrigramPredictor
from eliza.recorder import SessionRecorder, Store, Turn
from eliza.router import Router, default as default_router
from eliza.sequitur import Sequitur
from eliza.trajectory import detect_period


TRAJECTORY_WINDOW = 24


@dataclass
class StepResult:
    """The diagnostics produced by a single `step(ch)` call."""
    char: str
    chamber_from: Chamber
    chamber_to: Chamber
    chamber_from_word: str
    chamber_to_word: str
    orbit_to: str
    chirality: str
    fiber: str
    fiedler: float
    turbulence: float
    holonomy: HolonomyReading
    period: Optional[int]
    surprise: Optional[float]


class Engine:
    """The full eliza pipeline as a single composable object."""

    def __init__(
        self,
        store: Optional[Store] = None,
        router: Router = default_router,
        grammar_every: int = 0,
        vocab_size: int = 128,
        v4_canonicalize: bool = False,
    ) -> None:
        """Args:
          store: optional SQLite persistence.
          router: Char → Gen mapping (defaults to ord-mod-3).
          grammar_every: how often to feed an observation into the
            Sequitur grammars. 0 disables grammar induction entirely.
            1 = every char. Higher values subsample — the grammar still
            accumulates structure at coarser granularity.
          vocab_size: alphabet size for Laplace smoothing. 128 for ASCII
            text input, 256 for byte streams (binary files, ffmpeg pipes).
        """
        self.router = router
        self.grammar_every = grammar_every
        self._chars_since_grammar = 0
        self.vocab_size = vocab_size
        self.manifold = Manifold()
        self.cocycle = Cocycle(self.manifold)
        self.holonomy = Holonomy(self.manifold)
        self.predictor = TrigramPredictor(vocab_size=vocab_size)
        # Compression stats: total observations + cumulative surprise bits.
        self._n_obs = 0
        self._cum_surprise_bits = 0.0
        # Grammar-trigram: each "trigram piece" is a top-rule item
        # (terminal or nonterminal). The trigram now observes chunks of
        # input the grammar has factored, not raw symbols. As the grammar
        # thickens, each chunk covers more raw bits — effective context
        # length grows automatically with the SPPF.
        self._gt_context: Tuple[object, object] = (None, None)
        self._gt_counts: Dict[Tuple[object, object], Dict[object, int]] = {}
        self._gt_cum_surprise = 0.0
        # Orbit-indexed gram-tri: same (c1, c2) trigram, but extended with
        # the orbit at emission time as a third context dimension. The S3
        # "orientation" is the orbit selecting which of 6 conditional
        # distributions to use over the same (c1, c2) context.
        self._gt6_counts: Dict[
            Tuple[object, object, str], Dict[object, int]
        ] = {}
        # Tetrad reading: group top-rule positions into V₄ tetrads of
        # size 4. Position-in-tetrad ∈ {0,1,2,3} maps to V₄ slot label
        # ∈ {e, α, β, γ}. The S₃ orbit then ROTATES the slot, and there
        # are two competing readings of "which rotation":
        #
        #   gtV4a (absolute) — slot = orbit_now · V₄_canonical.
        #     The orbit gauges absolute orientation against e.
        #     "Where did we land."
        #
        #   gtV4d (delta) — slot = (orbit_now · orbit_at_tetrad_start⁻¹)
        #                          · V₄_canonical.
        #     The orbit measures the move from the tetrad's frame.
        #     "What move did we make."
        #
        # One of the two should beat gt; the user's intuition is unclear
        # which. Both share the same Sequitur build (binary) and read it
        # as V₄ tetrads at the top-rule level.
        self._gtV4a_counts: Dict[
            Tuple[object, object, str], Dict[object, int]
        ] = {}
        self._gtV4d_counts: Dict[
            Tuple[object, object, str], Dict[object, int]
        ] = {}
        # Top-rule emission counter (monotonic; resets are rare since
        # Sequitur replaces tails infrequently relative to emissions).
        # Used to compute position-in-tetrad = counter % 4.
        self._emission_count = 0
        # Orbit at the start of the current tetrad — the delta-frame.
        self._tetrad_frame_orbit: str = "e"
        # Per-orbit emission counts: when we're in orbit O and emit symbol s,
        # count[O][s] += 1. Used for orbit-conditional Huffman.
        self._orbit_emit_counts: Dict[str, Dict[object, int]] = {}
        # Char-level + orbit-level Sequitur grammars. v4_canonicalize on
        # the char grammar collapses V₄-orbit-equivalent digrams into one
        # rule with residue tags on NT references. Orbit grammar always
        # uses raw alphabet (string canonical_words for orbits).
        self.grammar_char = Sequitur(v4_canonicalize=v4_canonicalize)
        self.grammar_orbit = Sequitur()
        # Geometric SPPF: WH-addressed alternative, runs in parallel for
        # compression comparison. Built lazily because it needs the cocycle.
        from eliza.geo_sequitur import GeometricSPPF
        self.geo_sppf = GeometricSPPF(self.manifold, self.cocycle)
        # Coalgebraic codec: gt-over-V₄-slot, the substrate-honest
        # predictor where each unfold step IS the prediction step
        # (no separate trigram observing a separately-built grammar).
        # Runs alongside the others for comparison.
        from eliza.coalgebraic import CoalgebraicCodec
        self.coalg = CoalgebraicCodec(cocycle=self.cocycle)
        # Persistence (optional).
        self.store = store
        self.recorder = SessionRecorder(store) if store is not None else None
        if store is not None and self.recorder is not None:
            # Warm-start trigrams from store.
            self.predictor.load_counts(store.load_trigrams())
        # Walking state.
        self.current_chamber: Chamber = self.manifold.origin()
        self.trajectory: Deque[Chamber] = deque(
            [self.current_chamber], maxlen=TRAJECTORY_WINDOW
        )
        if self.recorder is not None:
            self.recorder.session_start_visit(
                word_str(self.manifold.shortlex_word(self.current_chamber))
            )

    # --- Per-char step ----------------------------------------------------

    def step(self, ch: str) -> StepResult:
        # 1. Surprise computed BEFORE updating context.
        surprise = self.predictor.surprise_bits(ch)
        # Track for compression stats. We count every symbol that has a
        # full 2-char context (skip the first two, where surprise is None).
        if surprise is not None:
            self._n_obs += 1
            self._cum_surprise_bits += surprise
        # 2. Route + walk.
        gen = self.router(ch)
        from_chamber = self.current_chamber
        from_word = word_str(self.manifold.shortlex_word(from_chamber))
        self.current_chamber = self._apply_generator(from_chamber, gen)
        to_word = word_str(self.manifold.shortlex_word(self.current_chamber))
        self.trajectory.append(self.current_chamber)
        # 2a. Coalgebraic codec: unfold one slot of the V₄ stream. This
        # step IS both the emission and the prediction (same compute).
        self.coalg.step(self.current_chamber)
        # 3. Orbit + cocycle info.
        info = self.cocycle.info(self.current_chamber)
        # 4. Holonomy at the new chamber.
        holonomy = self.holonomy.at(self.current_chamber)
        # 5. Period detection on the trajectory window.
        period = detect_period(list(self.trajectory))
        # 6. Update trigram model + persist.
        c1, c2 = self.predictor.context
        self.predictor.update(ch)
        if self.recorder is not None:
            self.recorder.record_turn(
                Turn(
                    n=0,  # SessionRecorder fills in monotonically
                    user_input=ch,
                    generator=gen,
                    chamber_from=from_word,
                    chamber_to=to_word,
                    bruhat=self.manifold.bruhat_distance(self.current_chamber),
                    fiedler=self.manifold.fiedler_value(self.current_chamber),
                    turbulence=self.manifold.turbulence_value(self.current_chamber),
                    holonomy_closes=holonomy.closes,
                    holonomy_target=word_str(
                        self.manifold.shortlex_word(holonomy.target)
                    ),
                    curvature=holonomy.curvature,
                    curvature_band=holonomy.band,
                    surprise=surprise,
                )
            )
            if c1 and c2:
                self.recorder.record_trigram(c1, c2, ch)
        # 7. Sequitur — observe at both alphabets, rate-limited.
        if self.grammar_every > 0:
            self._chars_since_grammar += 1
            if self._chars_since_grammar >= self.grammar_every:
                self._chars_since_grammar = 0
                self.grammar_char.observe(ch)
                self.grammar_orbit.observe(
                    self.cocycle.orbit_of(self.current_chamber)
                )
                # Grammar-trigram: observe the new top-rule tail as its own
                # Markov stream over (terminal ⊎ nonterminal).
                self._update_grammar_trigram()
                # Geometric SPPF: WH-addressed parallel grammar.
                self.geo_sppf.observe(ch)
        return StepResult(
            char=ch,
            chamber_from=from_chamber,
            chamber_to=self.current_chamber,
            chamber_from_word=from_word,
            chamber_to_word=to_word,
            orbit_to=info.canonical_word,
            chirality=info.chirality.name,
            fiber=info.fiber_label,
            fiedler=self.manifold.fiedler_value(self.current_chamber),
            turbulence=self.manifold.turbulence_value(self.current_chamber),
            holonomy=holonomy,
            period=period,
            surprise=surprise,
        )

    def _apply_generator(self, x: Chamber, gen_or_perm) -> Chamber:
        """Dispatch on what the router returned:
          * Gen (s1/s2/s3): apply via manifold.apply (Coxeter swap).
          * Chamber tuple: apply as right-multiplication via perm_compose
            — used by the nibble router for quaternion-shaped steps.
        """
        from eliza.manifold import apply
        from eliza.alphabets import perm_compose
        if isinstance(gen_or_perm, tuple):
            return perm_compose(x, gen_or_perm)
        return apply(gen_or_perm, x)

    # --- Grammar-trigram (production-rule predictor) --------------------

    def _update_grammar_trigram(self) -> None:
        """Observe the current top-rule tail and record (ctx → emit)
        triples for both:

          * the (c1, c2) gram-tri (expressive context, no constraint).
          * the (c1, c2, orbit) orbit-indexed gram-tri — the S₃
            orientation: same Sequitur structure, but one of 6
            conditional distributions selected by the current orbit.
            This captures structure the grammar hasn't yet absorbed;
            should help most when the grammar is small and lose
            relevance as the grammar matures.

        Also records (current_orbit, emit) for orbit-conditional Huffman
        and tracks orbit-transition rate as a grammar-maturity proxy.
        """
        top = self.grammar_char.top_rule()
        if not top:
            return
        emit_raw = top[-1]
        emit = emit_raw
        c1, c2 = self._gt_context
        orbit = self.cocycle.orbit_of(self.current_chamber)
        if c1 is not None and c2 is not None:
            inner = self._gt_counts.get((c1, c2), {})
            total = sum(inner.values())
            vocab = self.vocab_size + self.grammar_char.n_rules()
            p = (inner.get(emit, 0) + 0.5) / (total + 0.5 * vocab)
            surprise = -math.log2(p) if p > 0 else 32.0
            self._gt_cum_surprise += surprise
            self._gt_counts.setdefault((c1, c2), {})
            self._gt_counts[(c1, c2)][emit] = self._gt_counts[(c1, c2)].get(emit, 0) + 1
            # Orbit-indexed version (uses raw emit for comparability).
            self._gt6_counts.setdefault((c1, c2, orbit), {})
            self._gt6_counts[(c1, c2, orbit)][emit_raw] = (
                self._gt6_counts[(c1, c2, orbit)].get(emit_raw, 0) + 1
            )
            # Tetrad reading: position-in-tetrad → V₄ canonical slot label.
            # Capture the tetrad frame at every position-0 boundary.
            from eliza.alphabets import V4_LABELS
            pos_in_tetrad = self._emission_count % 4
            if pos_in_tetrad == 0:
                self._tetrad_frame_orbit = orbit
            v4_canonical = V4_LABELS[pos_in_tetrad]
            # Reading 1 — absolute: rotation = orbit_now.
            slot_abs = self.cocycle.s3_on_v4(orbit, v4_canonical)
            self._gtV4a_counts.setdefault((c1, c2, slot_abs), {})
            self._gtV4a_counts[(c1, c2, slot_abs)][emit_raw] = (
                self._gtV4a_counts[(c1, c2, slot_abs)].get(emit_raw, 0) + 1
            )
            # Reading 2 — delta: rotation = orbit_now · tetrad_frame_orbit⁻¹.
            relative = self.cocycle.relative_orbit(orbit, self._tetrad_frame_orbit)
            slot_dlt = self.cocycle.s3_on_v4(relative, v4_canonical)
            self._gtV4d_counts.setdefault((c1, c2, slot_dlt), {})
            self._gtV4d_counts[(c1, c2, slot_dlt)][emit_raw] = (
                self._gtV4d_counts[(c1, c2, slot_dlt)].get(emit_raw, 0) + 1
            )
        self._gt_context = (c2, emit_raw)  # context tracks raw (absolute residue)
        self._emission_count += 1
        # Per-orbit emission tally for orbit-conditional Huffman.
        bucket = self._orbit_emit_counts.setdefault(orbit, {})
        bucket[emit_raw] = bucket.get(emit_raw, 0) + 1

    # --- Compression metric ---------------------------------------------

    def compression_stats(self) -> dict:
        """Two complementary compression readouts:

        * trigram: -log₂ P(c | context). Captures local correlations.
        * grammar: cost to encode the input as the current Sequitur grammar
          — every rule body symbol + every top-rule symbol counts at
          `log₂(alphabet + n_rules)` bits each. This is what the
          accumulated SPPF buys you over the trigram: long-range structure
          captured as rule references. As the grammar thickens, this rate
          should drop below the trigram rate.
        """
        import math

        raw_bits = math.log2(self.vocab_size) if self.vocab_size > 1 else 1.0
        n_obs = self._n_obs

        # Trigram readout.
        bps_trigram = (
            self._cum_surprise_bits / n_obs if n_obs > 0 else raw_bits
        )

        # Grammar readout. Sums all rule body lengths (top rule + named rules);
        # each symbol takes log₂(alphabet + n_rules) bits. Under V₄
        # canonicalization, each NT reference additionally carries a
        # 2-bit residue tag (the V₄ transform from canonical to observed).
        n_rules = self.grammar_char.n_rules()
        if n_rules == 0:
            grammar_bits = float(n_obs) * raw_bits  # no compression yet
            sym_bits = raw_bits
        else:
            sym_bits = math.log2(self.vocab_size + n_rules)
            total_symbols = sum(
                len(body) for body in self.grammar_char.all_rules().values()
            )
            grammar_bits = total_symbols * sym_bits
            if self.grammar_char.v4_canonicalize:
                grammar_bits += 2.0 * self.grammar_char.n_nt_refs()
        bps_grammar = (
            grammar_bits / n_obs if n_obs > 0 else raw_bits
        )

        # Grammar-trigram readout. The honest metric is the cost to
        # encode the CURRENT top rule under the learned trigram model
        # (not the cumulative raw-symbol surprise, which over-counts
        # terminals that later got merged into NTs).
        gt_total_bits = self._grammar_trigram_cost_of_top()
        bps_gt = gt_total_bits / n_obs if n_obs > 0 else raw_bits

        # Orbit-indexed gram-tri variants:
        #   gt6  : (c1, c2, orbit)
        #   gtV4a: (c1, c2, S₃-act(orbit_now, V₄[i mod 4]))      — absolute
        #   gtV4d: (c1, c2, S₃-act(orbit_now·frame⁻¹, V₄[i mod 4])) — delta
        gt6_total_bits, gtV4a_bits, gtV4d_bits, cycling_rate = \
            self._gt_costs_of_top()
        bps_gt6 = gt6_total_bits / n_obs if n_obs > 0 else raw_bits
        bps_gtV4a = gtV4a_bits / n_obs if n_obs > 0 else raw_bits
        bps_gtV4d = gtV4d_bits / n_obs if n_obs > 0 else raw_bits

        # Huffman readout. Re-encodes the SPPF symbols at variable bit-
        # lengths driven by reference counts (marginal, no context).
        huffman_bits = self._huffman_grammar_bits()
        bps_huffman = huffman_bits / n_obs if n_obs > 0 else raw_bits

        # Orbit-conditional Huffman — the substrate move: each V₄-coset
        # gets its own code table, and emissions are encoded under the
        # table for the orbit they were emitted in. SPPF "rotates per
        # orbit" so symbols frequent in that orbit have short codes.
        orbit_huffman_bits, per_orbit = self._orbit_huffman_bits()
        bps_orbit_huff = orbit_huffman_bits / n_obs if n_obs > 0 else raw_bits

        # Geometric SPPF — Walsh-Hadamard-addressed grammar.
        geo_total_bits = self.geo_sppf.compression_bits()
        bps_geo = geo_total_bits / n_obs if n_obs > 0 else raw_bits

        # Coalgebraic codec — gt over V₄ slot stream. The substrate-honest
        # unification: one operation is both unfold and prediction.
        # NOTE: compresses a LOSSY PROJECTION (V₄ slot stream, alphabet=4),
        # so its ratio is reported relative to 2 bits/slot (the slot
        # alphabet's raw entropy), NOT to raw input bits. Lossless input
        # encoding requires an additional residual codec, not built yet.
        coalg_total_bits = self.coalg.compression_bits()
        bps_coalg = coalg_total_bits / n_obs if n_obs > 0 else 2.0
        coalg_raw_bits = 2.0  # log₂(|V₄|), the slot alphabet's raw budget

        return {
            "symbols": n_obs,
            "raw_bits_per_symbol": raw_bits,
            # Trigram on raw symbols (local arithmetic-coding cost).
            "bits_per_symbol": bps_trigram,
            "compressed_bits": self._cum_surprise_bits,
            "ratio": raw_bits / bps_trigram if bps_trigram > 0 else float("inf"),
            # Sequitur grammar (rule-table-derived).
            "grammar_bits_per_symbol": bps_grammar,
            "grammar_total_bits": grammar_bits,
            "grammar_ratio": (
                raw_bits / bps_grammar if bps_grammar > 0 else float("inf")
            ),
            "grammar_symbol_bits": sym_bits,
            "grammar_n_rules": n_rules,
            # Grammar-trigram (Markov over production rules).
            "gt_bits_per_symbol": bps_gt,
            "gt_total_bits": gt_total_bits,
            "gt_ratio": raw_bits / bps_gt if bps_gt > 0 else float("inf"),
            # Orbit-indexed gram-tri: (c1, c2, orbit) → emit. The S₃
            # orientation, capturing structure the grammar hasn't yet
            # absorbed; converges to gt as grammar matures.
            "gt6_bits_per_symbol": bps_gt6,
            "gt6_total_bits": gt6_total_bits,
            "gt6_ratio": raw_bits / bps_gt6 if bps_gt6 > 0 else float("inf"),
            # V₄-tetrad gram-tri, absolute reading.
            "gtV4a_bits_per_symbol": bps_gtV4a,
            "gtV4a_total_bits": gtV4a_bits,
            "gtV4a_ratio": raw_bits / bps_gtV4a if bps_gtV4a > 0 else float("inf"),
            # V₄-tetrad gram-tri, delta reading.
            "gtV4d_bits_per_symbol": bps_gtV4d,
            "gtV4d_total_bits": gtV4d_bits,
            "gtV4d_ratio": raw_bits / bps_gtV4d if bps_gtV4d > 0 else float("inf"),
            # Orbit-cycling rate. Approaches 5/6 ≈ 0.833 (uniform random
            # over 6 orbits) as the grammar absorbs predictability.
            "orbit_cycling_rate": cycling_rate,
            # Huffman over SPPF symbols (marginal, no context).
            "huffman_bits_per_symbol": bps_huffman,
            "huffman_total_bits": huffman_bits,
            "huffman_ratio": (
                raw_bits / bps_huffman if bps_huffman > 0 else float("inf")
            ),
            # Orbit-conditional Huffman — SPPF rotated per V₄-coset so
            # orbit-hot symbols get short codes within each orbit's tree.
            "orbit_huffman_bits_per_symbol": bps_orbit_huff,
            "orbit_huffman_total_bits": orbit_huffman_bits,
            "orbit_huffman_ratio": (
                raw_bits / bps_orbit_huff if bps_orbit_huff > 0 else float("inf")
            ),
            "orbit_huffman_per_orbit": per_orbit,
            # Geometric SPPF — WH-addressed (cell prefix + within-cell bits).
            "geo_total_bits": geo_total_bits,
            "geo_bits_per_symbol": bps_geo,
            "geo_ratio": (
                raw_bits / bps_geo if bps_geo > 0 else float("inf")
            ),
            "geo_n_rules": self.geo_sppf.n_rules(),
            "geo_cell_population": self.geo_sppf.cell_population(),
            # Coalgebraic codec — gt over V₄ slot stream. LOSSY projection;
            # ratio is over the 2-bit slot alphabet, not the input alphabet.
            "coalg_total_bits": coalg_total_bits,
            "coalg_bits_per_slot": bps_coalg,
            "coalg_raw_bits_per_slot": coalg_raw_bits,
            "coalg_slot_ratio": (
                coalg_raw_bits / bps_coalg if bps_coalg > 0 else float("inf")
            ),
            "coalg_n_contexts": self.coalg.n_contexts(),
        }

    def _grammar_trigram_cost_of_top(self) -> float:
        """Bits to encode the current top rule under the learned grammar-
        trigram. Each top-rule item costs -log₂ P(item | last 2 items).
        Items are terminals or NTs (= production rules). When V₄
        canonicalization is active, each NT additionally costs 2 bits
        of residue tag."""
        from eliza.sequitur import NT
        top = self.grammar_char.top_rule()
        if len(top) < 3:
            return 0.0
        cost = 0.0
        vocab = self.vocab_size + self.grammar_char.n_rules()
        for i in range(2, len(top)):
            ctx = (top[i - 2], top[i - 1])
            emit = top[i]
            inner = self._gt_counts.get(ctx, {})
            total = sum(inner.values())
            p = (inner.get(emit, 0) + 0.5) / (total + 0.5 * vocab)
            cost += -math.log2(p) if p > 0 else 32.0
        return cost

    def _gt_costs_of_top(self) -> Tuple[float, float, float, float]:
        """Bits to encode the top rule under three orbit-context variants,
        plus the power-weighted item-scale orbit-cycling rate.

        Returns (gt6_cost, gtV4a_cost, gtV4d_cost, cycling_rate):

          * gt6 uses (c1, c2, orbit) — orbit as a 6-way third context.
          * gtV4a (absolute): (c1, c2, slot) with
                slot = S₃-act(orbit_now, V4_LABELS[i % 4]).
            "Where did we land."
          * gtV4d (delta):    (c1, c2, slot) with
                slot = S₃-act(orbit_now · orbit_at_tetrad_start⁻¹,
                              V4_LABELS[i % 4]).
            "What move did we make from the tetrad's frame."

        All three share the chamber-replay through the top rule. The
        cycling rate is power-weighted (raw-char count as proxy for
        semantic weight) over orbit transitions at the top-rule-item
        scale.
        """
        top = self.grammar_char.top_rule()
        if len(top) < 3:
            return 0.0, 0.0, 0.0, 0.0
        gt6_cost = 0.0
        gtV4a_cost = 0.0
        gtV4d_cost = 0.0
        vocab = self.vocab_size + self.grammar_char.n_rules()
        from eliza.alphabets import ORIGIN, V4_LABELS
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
            # Tetrad position of item i within the top rule.
            pos_in_tetrad = i % 4
            v4_canonical = V4_LABELS[pos_in_tetrad]
            # Frame orbit = orbit at the start of the current tetrad.
            tetrad_start = i - pos_in_tetrad
            frame_orbit = self.cocycle.orbit_of(chambers_at[tetrad_start])
            slot_abs = self.cocycle.s3_on_v4(orbit, v4_canonical)
            slot_dlt = self.cocycle.s3_on_v4(
                self.cocycle.relative_orbit(orbit, frame_orbit),
                v4_canonical,
            )
            # gt6
            inner = self._gt6_counts.get((top[i - 2], top[i - 1], orbit), {})
            total = sum(inner.values())
            p = (inner.get(emit, 0) + 0.5) / (total + 0.5 * vocab)
            gt6_cost += -math.log2(p) if p > 0 else 32.0
            # gtV4a
            inner = self._gtV4a_counts.get((top[i - 2], top[i - 1], slot_abs), {})
            total = sum(inner.values())
            p = (inner.get(emit, 0) + 0.5) / (total + 0.5 * vocab)
            gtV4a_cost += -math.log2(p) if p > 0 else 32.0
            # gtV4d
            inner = self._gtV4d_counts.get((top[i - 2], top[i - 1], slot_dlt), {})
            total = sum(inner.values())
            p = (inner.get(emit, 0) + 0.5) / (total + 0.5 * vocab)
            gtV4d_cost += -math.log2(p) if p > 0 else 32.0
        # Power-weighted item-scale cycling.
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
        return gt6_cost, gtV4a_cost, gtV4d_cost, rate

    def _walk_symbol_for_top(self, sym, start) -> Tuple[Chamber, int]:
        """Walk a top-rule symbol (terminal or NT) from `start`, returning
        (end_chamber, n_raw_steps). NTs expand to their rule body
        recursively; n_raw_steps is the total raw-char count covered.

        Dispatches on the router's return type: Gen via manifold.apply,
        Chamber tuple via perm_compose (nibble mode)."""
        from eliza.manifold import apply as _apply
        from eliza.alphabets import perm_compose
        from eliza.sequitur import NT as _NT
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
        # Terminal: apply the router's generator/perm.
        action = self.router(sym) if isinstance(sym, str) and len(sym) == 1 else None
        if action is None:
            return start, 0
        if isinstance(action, tuple):
            return perm_compose(start, action), 1
        return _apply(action, start), 1

    @staticmethod
    def _huffman_code_lengths(counts: Dict[object, int]) -> Dict[object, int]:
        """Build a Huffman code table from a symbol-count dict. Returns
        a {symbol: code_length} map. Empty input → empty map."""
        import heapq

        if not counts:
            return {}
        if len(counts) == 1:
            return {next(iter(counts)): 1}
        tie = [0]
        heap = []
        for sym, c in counts.items():
            heapq.heappush(heap, (c, tie[0], ("L", sym)))
            tie[0] += 1
        while len(heap) > 1:
            a = heapq.heappop(heap)
            b = heapq.heappop(heap)
            heapq.heappush(heap, (a[0] + b[0], tie[0], ("N", a[2], b[2])))
            tie[0] += 1
        lengths: Dict[object, int] = {}

        def walk(node, depth):
            if node[0] == "L":
                lengths[node[1]] = max(depth, 1)
            else:
                walk(node[1], depth + 1)
                walk(node[2], depth + 1)

        walk(heap[0][2], 0)
        return lengths

    def _orbit_huffman_bits(self) -> Tuple[float, Dict[str, int]]:
        """Per-orbit Huffman: each V₄-coset has its own code table built
        from the symbols emitted while in that orbit. Returns
        (total_bits, {orbit: bits}). Symbols frequent in an orbit get
        short codes within that orbit's tree — the substrate's
        'rotate the SPPF per orbit so orbit-hot codes are shallow.'"""
        total = 0.0
        per_orbit: Dict[str, int] = {}
        for orbit, counts in self._orbit_emit_counts.items():
            lengths = self._huffman_code_lengths(counts)
            orbit_bits = sum(lengths[s] * c for s, c in counts.items())
            per_orbit[orbit] = orbit_bits
            total += orbit_bits
        return total, per_orbit

    def _huffman_grammar_bits(self) -> float:
        """Bits to encode the grammar + top rule using Huffman codes on
        symbol reference counts. Each symbol (terminal or NT) gets a
        variable-length code whose length is inversely log-proportional
        to its frequency across all rule bodies. Frequent symbols get
        short codes — the deflate-style 'rotate the SPPF so most-likely
        leaves have short paths' that the user identified.
        """
        import heapq

        # Count references to each symbol across ALL rule bodies (top + named).
        refs: Dict[object, int] = {}
        for rule in self.grammar_char.rules.values():
            for node in rule.body_iter():
                refs[node.sym] = refs.get(node.sym, 0) + 1
        if not refs:
            return 0.0
        if len(refs) == 1:
            # Single symbol → 1 bit per occurrence by convention.
            return float(sum(refs.values()))
        # Huffman tree construction. Heap entries: (count, tiebreaker, payload).
        tie = [0]
        heap = []
        for sym, count in refs.items():
            heapq.heappush(heap, (count, tie[0], ("L", sym)))
            tie[0] += 1
        while len(heap) > 1:
            c1 = heapq.heappop(heap)
            c2 = heapq.heappop(heap)
            heapq.heappush(
                heap,
                (c1[0] + c2[0], tie[0], ("N", c1[2], c2[2])),
            )
            tie[0] += 1
        # Walk to extract code lengths.
        lengths: Dict[object, int] = {}

        def walk(node, depth):
            if node[0] == "L":
                lengths[node[1]] = max(depth, 1)
            else:
                walk(node[1], depth + 1)
                walk(node[2], depth + 1)

        walk(heap[0][2], 0)
        return float(sum(lengths[sym] * count for sym, count in refs.items()))

    # --- Bulk run ---------------------------------------------------------

    def run(self, text: str) -> Tuple[Chamber, list]:
        results = [self.step(ch) for ch in text]
        return self.current_chamber, results

    # --- Lifecycle --------------------------------------------------------

    def end(self) -> None:
        if self.recorder is not None:
            self.recorder.session_end()
        if self.store is not None:
            self.store.close()
