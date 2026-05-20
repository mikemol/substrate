"""Eliza.GeoSequitur — Walsh-Hadamard-addressed SPPF.

Replaces the digram-uniqueness invariant with geometric placement:

  * Each rule has a 3-D spectral position from its end-chamber's
    Laplacian-mode coordinates (Fiedler, mode-2, mode-3).
  * At each emission, the current chamber's orbit supplies a 3-bit
    F₂³ vector (Fano selection / Walsh-Hadamard row). This 3-bit
    vector sign-flips the 3 position axes — the "convolution" of
    Sequitur's mapping into the rule's spectral position.
  * 2D matrix imagery: the convoluted (axis-1, axis-2) coordinates
    Morton-interleave into a 2-bit address for the lower-left
    triangle (binary tree of cells). The convoluted axis-3 sign +
    chamber chirality (parity) give 2 more bits for the upper-right
    triangle. Together: 4 Walsh-Hadamard bits, 16 cells.
  * Within each cell, exact digram match preserves correctness of
    grammar reconstruction.

No heuristic gating — placement is determined entirely by spectral
geometry + the predictor's gauge selection. The compression cost is
4 cell-address bits + bits-to-distinguish-within-cell, with the
geometric structure inducing variable cell occupancy that mirrors
the input's structural content.

Cross-references:
  * Substrate.Geometry.HodgeDim3 — V₄-plane + chirality-axis decomp.
  * Substrate.Algebra.F2.HodgeDim4.HodgeStar — order-2 involution = parity bit.
  * Substrate.Cocycles.V4Signature — (orbit, fiber) split = (cell, within-cell).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from eliza.alphabets import Chamber, Gen, GENERATORS, ORIGIN
from eliza.manifold import Manifold, apply, word_str
from eliza.orbit import Cocycle


@dataclass(frozen=True)
class NT:
    """Nonterminal reference (= production rule reference)."""
    rule_id: int

    def __repr__(self) -> str:
        return f"R{self.rule_id}"


# --- Terminal → Gen mapping (matches the project-wide router) -------------


def _generator_for_terminal(sym: Any) -> Optional[Gen]:
    """Return the Coxeter generator that a terminal symbol emits, or
    None if `sym` is not a single-character terminal."""
    if not isinstance(sym, str) or len(sym) != 1:
        return None
    return list(GENERATORS)[ord(sym) % 3]


# --- The SPPF -------------------------------------------------------------


class GeometricSPPF:
    """Walsh-Hadamard-addressed Sequitur-style grammar over a single
    coalgebraic stream.

    Public API mirrors the existing Sequitur:
      * observe(terminal): append + canonicalise.
      * top_rule(): the current encoded sequence (list of terminals + NTs).
      * n_rules(): count of induced non-top rules.
      * all_rules(): full rule-id → body dict.
      * format_rule, top_rules: pretty-print helpers.

    Additional substrate-aware methods:
      * cell_of(digram): the 4-bit WH cell that hosts this digram.
      * cell_population(): {cell_id → number of rules}.
      * compression_bits(): bits to encode the input under the current grammar.
    """

    NUM_CELLS = 16

    def __init__(self, manifold: Manifold, cocycle: Cocycle) -> None:
        self.manifold = manifold
        self.cocycle = cocycle
        # Per-orbit 2D pan offset. The "fixed 3D SPPF" gets PROJECTED
        # to 2D via the Hadamard construction; the orbit translates
        # (pans) the 2D viewpoint. Each orbit's pan = its canonical
        # chamber's first two spectral coordinates. Same rule observed
        # in the same orbit → same panned position → same cell.
        self._orbit_pan: Dict[str, Tuple[float, float]] = {}
        # Cache eigenvector columns for modes 1, 2, 3 (skip mode 0 trivial).
        self._mode3 = np.asarray(manifold._eigenvectors[:, 3]).flatten()
        # Compute orbit pan offsets: each orbit's canonical chamber's (axis-1,
        # axis-2) projection. The pan translates the 2D view per orbit.
        for orbit_word in cocycle.orbits():
            members = list(cocycle.coset_members(orbit_word))
            if not members:
                self._orbit_pan[orbit_word] = (0.0, 0.0)
                continue
            # Use the orbit's canonical (= smallest-by-shortlex) chamber.
            info = cocycle.info(members[0])
            canonical = info.canonical
            pos = (
                manifold.fiedler_value(canonical),
                manifold.turbulence_value(canonical),
            )
            self._orbit_pan[orbit_word] = pos
        # Rules. 0 is the top rule (the input encoded so far).
        self.rules: Dict[int, List[Any]] = {0: []}
        self._uses: Dict[int, int] = {0: 1}
        # End-chamber per rule (where applying the rule lands you when
        # started from origin). Used to compute the rule's position.
        self._end_chamber: Dict[int, Chamber] = {0: ORIGIN}
        self._next_id = 1
        # WH cells: 16 buckets, each maps {digram_key → rule_id}.
        self.cells: List[Dict[Tuple[Any, Any], int]] = [
            {} for _ in range(self.NUM_CELLS)
        ]
        # Per-cell digram counters for digrams not yet promoted to rules.
        # A digram gets promoted to a rule on its SECOND occurrence in
        # the same cell (Sequitur's digram-uniqueness invariant, scoped
        # per WH cell).
        self._cell_seen: List[Dict[Tuple[Any, Any], int]] = [
            {} for _ in range(self.NUM_CELLS)
        ]
        # Track which cell each rule lives in.
        self._rule_cell: Dict[int, int] = {}
        # Compression accounting.
        self._cum_bits = 0.0
        # Trailing chamber: the chamber reached by walking the top rule
        # from origin. Updated as we emit.
        self._top_end_chamber: Chamber = ORIGIN

    # --- 3-D spectral position lookup -------------------------------------

    def _spectral_3d(self, chamber: Chamber) -> Tuple[float, float, float]:
        i = self.manifold.node_index(chamber)
        return (
            self.manifold.fiedler_value(chamber),
            self.manifold.turbulence_value(chamber),
            float(self._mode3[i]),
        )

    # --- Walking the grammar -----------------------------------------------

    def _walk_symbol(self, sym: Any, start: Chamber) -> Chamber:
        """End chamber after applying `sym` from `start`."""
        if isinstance(sym, NT):
            return self._end_chamber.get(sym.rule_id, start)
        gen = _generator_for_terminal(sym)
        if gen is None:
            return start
        # The end chamber of a generator g applied at any chamber x is
        # apply(g, x). For terminals, equivalent to walking one step.
        return apply(gen, start)

    def _digram_end(
        self, sym1: Any, sym2: Any, start: Chamber
    ) -> Chamber:
        """End chamber after applying (sym1, sym2) from `start`."""
        return self._walk_symbol(sym2, self._walk_symbol(sym1, start))

    # --- The Walsh-Hadamard signature -------------------------------------

    def signature(
        self,
        sym1: Any,
        sym2: Any,
        current_chamber: Chamber,
    ) -> int:
        """Compute the 4-bit cell index for digram (sym1, sym2) at
        `current_chamber`.

        Construction (substrate-honest):
          1. Walk the digram → end chamber. The end chamber's 3-D
             spectral position (axis-1, axis-2, axis-3) is the rule's
             *fixed* position in the SPPF.
          2. PROJECT the SPPF into 2D via the (axis-1, axis-2)
             Hadamard projection (axis-3 stays as the normal).
          3. PAN the 2D view by the current orbit's pan vector. The
             pan = the orbit's canonical chamber's (axis-1, axis-2).
             Same rule + same orbit = same panned position = same cell.
          4. The 3rd-axis sign decides axis-1/axis-2 swap order — the
             "3rd dim bit picks which of first two is primary" rule.
          5. Pack signed (axis-1, axis-2) bits + 3rd-axis sign +
             chirality parity → 4-bit cell.
        """
        end = self._digram_end(sym1, sym2, current_chamber)
        coords = self._spectral_3d(end)
        # Pan by orbit. The 3rd axis is preserved (the normal).
        orbit_word = self.cocycle.orbit_of(current_chamber)
        pan = self._orbit_pan.get(orbit_word, (0.0, 0.0))
        px = coords[0] - pan[0]
        py = coords[1] - pan[1]
        pz = coords[2]
        # 3rd-dim sign decides axis-1/axis-2 application order.
        if pz < 0:
            px, py = py, px
        sig = 0
        if px >= 0: sig |= 1
        if py >= 0: sig |= 2
        if pz >= 0: sig |= 4
        if self.cocycle.chirality_of(end).name == "odd":
            sig |= 8
        return sig

    # --- The single public method: observe one terminal --------------------

    def observe(self, terminal: Any) -> None:
        """Extend the top rule by one terminal and canonicalise.

        Classical Sequitur's digram-uniqueness scoped per WH cell:
          * If the trailing digram has an existing rule in its cell,
            reuse it (replace digram → NT reference).
          * If the digram has been seen ONCE in its cell, promote on
            this 2nd occurrence: create a new rule, replace this
            occurrence with the NT.
          * Otherwise: record as seen-once, no further action.

        Each replacement may form a new trailing digram, which is
        checked in the same loop.
        """
        top = self.rules[0]
        top.append(terminal)
        self._top_end_chamber = self._walk_symbol(
            terminal, self._top_end_chamber
        )
        while len(top) >= 2:
            sym1, sym2 = top[-2], top[-1]
            start_chamber = self._walk_prefix(top[:-2])
            sig = self.signature(sym1, sym2, start_chamber)
            cell = self.cells[sig]
            seen = self._cell_seen[sig]
            digram_key = (sym1, sym2)
            if digram_key in cell:
                # Existing rule in this cell. Reuse.
                rid = cell[digram_key]
                self._uses[rid] = self._uses.get(rid, 0) + 1
                top.pop()
                top.pop()
                top.append(NT(rid))
                continue
            if seen.get(digram_key, 0) >= 1:
                # Second occurrence in this cell. Promote to rule.
                rid = self._next_id
                self._next_id += 1
                self.rules[rid] = [sym1, sym2]
                self._uses[rid] = 2  # the prior + this occurrence
                self._end_chamber[rid] = self._digram_end(
                    sym1, sym2, ORIGIN
                )
                cell[digram_key] = rid
                self._rule_cell[rid] = sig
                del seen[digram_key]
                top.pop()
                top.pop()
                top.append(NT(rid))
                continue
            # First occurrence in this cell. Record and break.
            seen[digram_key] = 1
            break

    def _walk_prefix(self, prefix: List[Any]) -> Chamber:
        """Walk a prefix of symbols from origin to its end chamber."""
        x: Chamber = ORIGIN
        for s in prefix:
            x = self._walk_symbol(s, x)
        return x

    # --- Compression metric -----------------------------------------------

    def compression_bits(self) -> float:
        """Bits to encode the current top rule under cell-Huffman.

        Each NT reference costs 4 cell-address bits + Huffman code-length
        within its cell. Within-cell Huffman weights each rule by its
        use count, so frequent rules in heavily-populated cells get short
        codes (= AVL-style: high-traffic nodes near the root).
        """
        if not self.rules[0]:
            return 0.0
        terminals = {
            s for body in self.rules.values()
            for s in body if not isinstance(s, NT)
        }
        term_bits = max(math.log2(max(len(terminals), 2)), 1.0)
        cell_addr_bits = math.log2(self.NUM_CELLS)  # 4 bits
        # Per-cell Huffman code-length tables by use count.
        cell_lengths: Dict[int, Dict[int, int]] = {}
        for cell_id, cell in enumerate(self.cells):
            if not cell:
                cell_lengths[cell_id] = {}
                continue
            weighted = [
                (self._uses.get(rid, 1), rid) for _, rid in cell.items()
            ]
            cell_lengths[cell_id] = self._huffman_lengths(weighted)
        total = 0.0
        for s in self.rules[0]:
            if isinstance(s, NT):
                cell = self._rule_cell.get(s.rule_id, 0)
                length = cell_lengths.get(cell, {}).get(s.rule_id, 1)
                total += cell_addr_bits + length
            else:
                total += term_bits
        # Plus grammar table.
        for rid, body in self.rules.items():
            if rid == 0:
                continue
            for s in body:
                if isinstance(s, NT):
                    cell = self._rule_cell.get(s.rule_id, 0)
                    length = cell_lengths.get(cell, {}).get(s.rule_id, 1)
                    total += cell_addr_bits + length
                else:
                    total += term_bits
        return total

    @staticmethod
    def _huffman_lengths(
        weighted: List[Tuple[int, int]],
    ) -> Dict[int, int]:
        """weighted: [(use_count, rule_id), ...]. Returns {rule_id: code_length}."""
        import heapq

        if not weighted:
            return {}
        if len(weighted) == 1:
            return {weighted[0][1]: 1}
        tie = [0]
        heap = []
        for w, rid in weighted:
            heapq.heappush(heap, (w, tie[0], ("L", rid)))
            tie[0] += 1
        while len(heap) > 1:
            a = heapq.heappop(heap)
            b = heapq.heappop(heap)
            heapq.heappush(heap, (a[0] + b[0], tie[0], ("N", a[2], b[2])))
            tie[0] += 1
        lengths: Dict[int, int] = {}

        def walk(node, depth):
            if node[0] == "L":
                lengths[node[1]] = max(depth, 1)
            else:
                walk(node[1], depth + 1)
                walk(node[2], depth + 1)

        walk(heap[0][2], 0)
        return lengths

    # --- Observation diagnostics ------------------------------------------

    def top_rule(self) -> List[Any]:
        return list(self.rules[0])

    def n_rules(self) -> int:
        return len(self.rules) - 1

    def all_rules(self) -> Dict[int, List[Any]]:
        return {k: list(v) for k, v in self.rules.items()}

    def rule_uses(self, rule_id: int) -> int:
        return self._uses.get(rule_id, 0)

    def cell_population(self) -> Dict[int, int]:
        return {i: len(c) for i, c in enumerate(self.cells)}

    def format_rule(self, rule_id: int) -> str:
        body = self.rules.get(rule_id, [])
        parts: List[str] = []
        for s in body:
            if isinstance(s, NT):
                parts.append(f"R{s.rule_id}")
            else:
                parts.append(repr(s))
        cell = self._rule_cell.get(rule_id, 0)
        cell_label = f"cell={cell:04b}"
        return (
            f"R{rule_id} [{cell_label}] → {' '.join(parts) or 'ε'}  "
            f"(uses={self._uses.get(rule_id, 0)})"
        )

    def top_rules(self, n: int = 5) -> List[str]:
        candidates = [
            (rid, self._uses.get(rid, 0)) for rid in self.rules if rid != 0
        ]
        candidates.sort(key=lambda kv: -kv[1])
        return [self.format_rule(rid) for rid, _ in candidates[:n]]
