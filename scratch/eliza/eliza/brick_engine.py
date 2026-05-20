"""Eliza.BrickEngine — the new Engine.step body, expressed as a layer DAG.

Per the DBE trace in DATAFLOW_REMODEL.md, Engine.step has 19 information
flows and 13 active bricks. The flows form a fan-out DAG (the chamber
walk's new-chamber output feeds 5 downstream consumers, etc.), not a
strict linear chain.

BrickEngine routes each layer's input from the available data sources
(input symbol, chamber observation, orbit, ...) and aggregates stats
at the end. This is slice 13's runtime: a DAG of layers conforming to
the Brick protocol.

For the strict-Pipeline case (linear D-flow), see `pipeline.Pipeline`.
This module handles the more general fan-out case the actual engine
needs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from eliza.brick import Brick
from eliza.coalgebraic import CoalgebraicCodec
from eliza.geo_sequitur import GeometricSPPF
from eliza.holonomy import Holonomy
from eliza.layers import (
    ChamberLayer, ChamberObservation, CoalgLayer, GeoSppfLayer,
    GtTrigramLayer, HuffmanLayer,
    PredictorLayer, SequiturCharLayer, SequiturOrbitLayer,
)
import math
from eliza.manifold import Manifold
from eliza.orbit import Cocycle
from eliza.predictor import TrigramPredictor
from eliza.router import Router, default as default_router
from eliza.sequitur import Sequitur


@dataclass
class BrickEngine:
    """A DAG of layers, routed by the per-step input.

    For each input symbol:
      * ChamberLayer consumes the char, produces a ChamberObservation.
      * PredictorLayer consumes the char (separate input stream).
      * SequiturCharLayer consumes the char.
      * SequiturOrbitLayer consumes the chamber observation's orbit.
      * GeoSppfLayer consumes the char.
      * CoalgLayer consumes the post-walk chamber.

    Each layer is a Brick conforming to the protocol. Stats from every
    layer are merged into a single dict on `compression_stats()`.
    """
    manifold: Manifold = field(default_factory=Manifold)
    cocycle: Cocycle = field(init=False)
    holonomy: Holonomy = field(init=False)
    router: Router = field(default=default_router)
    vocab_size: int = 128

    chamber: ChamberLayer = field(init=False)
    predictor_layer: PredictorLayer = field(init=False)
    seq_char: Any = field(init=False)
    seq_orbit: Any = field(init=False)
    geo: GeoSppfLayer = field(init=False)
    coalg: CoalgLayer = field(init=False)
    gt: GtTrigramLayer = field(init=False)
    huffman: HuffmanLayer = field(init=False)
    grammar_every: int = 1
    _chars_since_grammar: int = 0

    def __post_init__(self):
        self.cocycle = Cocycle(self.manifold)
        self.holonomy = Holonomy(self.manifold)
        self.chamber = ChamberLayer(
            manifold=self.manifold, cocycle=self.cocycle,
            holonomy=self.holonomy, router=self.router,
        )
        self.predictor_layer = PredictorLayer(
            predictor=TrigramPredictor(vocab_size=self.vocab_size)
        )
        self.seq_char = SequiturCharLayer(grammar=Sequitur())
        self.seq_orbit = SequiturOrbitLayer(grammar=Sequitur())
        self.geo = GeoSppfLayer(sppf=GeometricSPPF(self.manifold, self.cocycle))
        self.coalg = CoalgLayer(codec=CoalgebraicCodec(cocycle=self.cocycle))
        self.gt = GtTrigramLayer(
            cocycle=self.cocycle,
            grammar_char=self.seq_char.grammar,
            predictor=self.predictor_layer.predictor,
            router=self.router,
            manifold=self.manifold,
        )
        self.huffman = HuffmanLayer(
            grammar_char=self.seq_char.grammar,
            predictor=self.predictor_layer.predictor,
            gt_layer=self.gt,
        )

    @property
    def layers(self) -> List[Brick]:
        """The 8 layers, in DAG-topological order."""
        return [
            self.chamber, self.predictor_layer, self.seq_char,
            self.seq_orbit, self.geo, self.coalg, self.gt, self.huffman,
        ]

    def step(self, ch: str) -> ChamberObservation:
        """Process one input symbol through the DAG."""
        # 1. Surprise BEFORE update (PredictorLayer.step does both).
        self.predictor_layer.step(ch, self.predictor_layer.predictor)
        # 2. Chamber walk + cocycle + holonomy.
        obs, _ = self.chamber.step(ch, self.chamber.state)
        # 3. Coalg: consumes post-walk chamber.
        self.coalg.step(obs.chamber_to, self.coalg.codec)
        # 4. Grammar observers (rate-limited).
        if self.grammar_every > 0:
            self._chars_since_grammar += 1
            if self._chars_since_grammar >= self.grammar_every:
                self._chars_since_grammar = 0
                self.seq_char.step(ch, self.seq_char.grammar)
                self.seq_orbit.step(obs.orbit.canonical_word, self.seq_orbit.grammar)
                # gt update reads grammar_char's top + current_chamber.
                self.gt.step(obs.chamber_to, self.gt)
                self.geo.step(ch, self.geo.sppf)
        return obs

    def show(self, path: str = None) -> str:
        """Auto-generate a Mermaid flowchart of the BrickEngine DAG.

        Unlike `pipeline.show`, which assumes a linear chain, this
        renders the fan-out structure: each layer is a hexagon node,
        state stores are cylinders, and edges are labelled by the
        D-edge type.

        Output is structurally equivalent to the hand-drawn diagram
        in DATAFLOW_REMODEL.md (modulo cosmetic layout).
        """
        lines = ["flowchart TB"]
        lines.extend([
            "    classDef input fill:#cfc,stroke:#080,stroke-width:2px",
            "    classDef output fill:#fcc,stroke:#800,stroke-width:2px",
            "    classDef state fill:#ccf,stroke:#008",
            "    classDef sread fill:#ffe,stroke:#aa0",
            "    classDef swrite fill:#fee,stroke:#a00",
            "    classDef chooser fill:#fef,stroke:#a0a",
            "    classDef merger fill:#eef,stroke:#00a",
            "    classDef dispatch fill:#eff,stroke:#0aa",
            "    classDef pure fill:#eee,stroke:#888",
            "",
        ])
        from eliza.brick import Witnessing as W
        cls_map = {
            W.D_TO_S: "swrite", W.S_TO_D: "sread",
            W.D_TO_C: "chooser", W.C_TO_D: "merger",
            W.S_TO_C: "dispatch", W.C_TO_S: "swrite",
        }
        # Boundary nodes.
        lines.append("    ch([Input: ch]):::input")
        # State stores (one per layer's S carrier).
        lines.extend([
            "    pred[(Predictor counts)]:::state",
            "    chamber_s[(current chamber)]:::state",
            "    traj[(trajectory)]:::state",
            "    gchar[(grammar_char)]:::state",
            "    gorbit[(grammar_orbit)]:::state",
            "    gtc[(gt counts)]:::state",
            "    geo_s[(GeoSPPF)]:::state",
            "    coalg_s[(Coalg)]:::state",
            "",
        ])
        # Layer nodes (hexagons, colored by witnessing).
        layer_ids = {}
        for i, layer in enumerate(self.layers):
            node_id = f"L{i}"
            layer_ids[layer.name] = node_id
            cls = cls_map.get(layer.witnesses, "pure")
            label = f"{layer.name}<br/>{layer.witnesses.value}"
            lines.append(f"    {node_id}{{{{{label}}}}}:::{cls}")
        lines.append("")
        # Data-flow edges (fan-out from `ch` and from chamber).
        lines.append("    ch --> L1")  # PredictorLayer
        lines.append("    ch --> L0")  # ChamberLayer
        lines.append("    ch --> L2")  # SequiturCharLayer
        lines.append("    ch --> L4")  # GeoSppfLayer
        lines.append("    L0 -.read.-> chamber_s")
        lines.append("    L0 -->|chamber'| chamber_s")
        lines.append("    L0 -->|orbit| L3")  # → SequiturOrbitLayer
        lines.append("    L0 -->|chamber| L5")  # → CoalgLayer
        lines.append("    L0 -->|chamber| L6")  # → GtTrigramLayer
        lines.append("    L0 -->|chamber| traj")
        lines.append("    L1 -.read.-> pred")
        lines.append("    L1 -->|counts'| pred")
        lines.append("    L2 -->|rules'| gchar")
        lines.append("    L3 -->|rules'| gorbit")
        lines.append("    L4 -->|cells'| geo_s")
        lines.append("    L5 -->|slot'| coalg_s")
        lines.append("    L6 -->|gt counts'| gtc")
        lines.append("    L7 -.read.-> gchar")
        lines.append("    L7 -.read.-> gtc")
        # Stats sink.
        lines.append("    stats([compression_stats]):::output")
        for i, _ in enumerate(self.layers):
            lines.append(f"    L{i} -.stats.-> stats")
        src = "\n".join(lines)
        if path is not None:
            content = (f"# BrickEngine DAG\n\n```mermaid\n{src}\n```\n"
                       if path.endswith(".md") else src)
            with open(path, "w") as f:
                f.write(content)
        return src

    def compression_stats(self) -> Dict[str, Any]:
        """Mirror Engine.compression_stats: aggregate + reconcile to the
        canonical n_obs (predictor's count of symbols with full context)."""
        out: Dict[str, Any] = {}
        for layer in self.layers:
            out.update(layer.stats())
        raw_bits = math.log2(self.vocab_size) if self.vocab_size > 1 else 1.0
        n_obs = self.predictor_layer._n_obs
        # Reconcile BPS / ratio keys against the canonical denominator.
        # Engine.compression_stats normalises by predictor._n_obs everywhere,
        # not by each layer's own emission count.
        for total_key, bps_key, ratio_key in [
            ("gt_total_bits", "gt_bits_per_symbol", "gt_ratio"),
            ("gt6_total_bits", "gt6_bits_per_symbol", "gt6_ratio"),
            ("gtV4a_total_bits", "gtV4a_bits_per_symbol", "gtV4a_ratio"),
            ("gtV4d_total_bits", "gtV4d_bits_per_symbol", "gtV4d_ratio"),
            ("huffman_total_bits", "huffman_bits_per_symbol", "huffman_ratio"),
            ("orbit_huffman_total_bits", "orbit_huffman_bits_per_symbol", "orbit_huffman_ratio"),
        ]:
            if total_key in out:
                bps = out[total_key] / n_obs if n_obs > 0 else raw_bits
                out[bps_key] = bps
                out[ratio_key] = raw_bits / bps if bps > 0 else float("inf")
        # Coalg: bps relative to 2-bit slot raw, ratio against same.
        if "coalg_total_bits" in out:
            coalg_raw = 2.0
            bps = out["coalg_total_bits"] / n_obs if n_obs > 0 else coalg_raw
            out["coalg_bits_per_slot"] = bps
            out["coalg_raw_bits_per_slot"] = coalg_raw
            out["coalg_slot_ratio"] = coalg_raw / bps if bps > 0 else float("inf")
        # Geo: also ratio.
        if "geo_total_bits" in out:
            bps = out["geo_total_bits"] / n_obs if n_obs > 0 else raw_bits
            out["geo_bits_per_symbol"] = bps
            out["geo_ratio"] = raw_bits / bps if bps > 0 else float("inf")
        # Grammar storage cost (= Engine's grammar_total_bits + ratio + ...).
        n_rules = self.seq_char.grammar.n_rules()
        if n_rules == 0:
            grammar_bits = float(n_obs) * raw_bits
            sym_bits = raw_bits
        else:
            sym_bits = math.log2(self.vocab_size + n_rules)
            total_symbols = sum(
                len(body) for body in self.seq_char.grammar.all_rules().values()
            )
            grammar_bits = total_symbols * sym_bits
        out["grammar_bits_per_symbol"] = grammar_bits / n_obs if n_obs > 0 else raw_bits
        out["grammar_total_bits"] = grammar_bits
        out["grammar_ratio"] = (
            raw_bits / out["grammar_bits_per_symbol"]
            if out["grammar_bits_per_symbol"] > 0 else float("inf")
        )
        out["grammar_symbol_bits"] = sym_bits
        out["grammar_n_rules"] = n_rules
        return out
