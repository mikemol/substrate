"""Eliza.Coalgebraic — codec over the V₄ slot stream.

The slot stream is the V₄ projection of the chamber walk:

    slot_i = S₃-act(orbit(chamber_i), fiber(chamber_i)) ∈ V₄

The codec is a Markov-3 over the V₄ alphabet — gt-over-slot — trained
online. The coalgebraic property: at each chamber update, ONE operation
both emits a slot (the unfold step) and incurs cost -log P(slot | last
two slots) (the prediction step). They are the same compute.

THE PROJECTION IS LOSSY. The slot stream is a 4-way summary of the
chamber, which is a function of the symbol stream. To compress the
INPUT losslessly, two layers are required:

  Layer 1 — slot stream codec (this module).
    Encodes V₄ slot stream. Raw cost: log₂(4) = 2 bits/slot.
    Achieves some compression by capturing slot-stream structure.

  Layer 2 — residual codec (NOT YET BUILT).
    Encodes (input_symbol | slot_just_produced). The slot tells us
    "the chamber landed in this V₄ position"; the residual disambiguates
    among input symbols that could produce that chamber.
    For bit mode (vocab=2, ord_mod_3 router): slots are constant `e`
    because s1/s2 stay within S₃ ⊂ S₄, so the residual carries 100% of
    the input information.
    For text/binary: slots vary; residual carries the within-slot entropy.

The honest input compression ratio is `(slot_bits + residual_bits) /
raw_input_bits`. This module reports only slot_bits; it is NOT directly
comparable to input-stream codecs (gt, huffman, etc.) until Layer 2 is
added.

The reported ratio in this module is `2.0 / bits_per_slot` — compression
relative to the slot alphabet's raw entropy, not the input's.

Decodability: with adaptive arithmetic coding the bit stream decodes
to the slot stream losslessly. Input recovery requires Layer 2.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from eliza.alphabets import Chamber, V4_LABELS
from eliza.orbit import Cocycle


@dataclass
class CoalgebraicCodec:
    """gt-over-V₄-slot codec, trained online from chamber observations."""

    cocycle: Cocycle
    alphabet_size: int = len(V4_LABELS)  # 4
    alpha: float = 0.5
    _gt_counts: Dict[Tuple[str, str], Dict[str, int]] = field(default_factory=dict)
    _gt_context: Tuple[Optional[str], Optional[str]] = (None, None)
    _cum_bits: float = 0.0
    _n_steps: int = 0
    _slot_stream: List[str] = field(default_factory=list)

    def step(self, chamber: Chamber) -> float:
        """Project chamber → slot, predict + train, return bits incurred."""
        orbit = self.cocycle.orbit_of(chamber)
        fiber = self.cocycle.fiber_of(chamber)
        slot = self.cocycle.s3_on_v4(orbit, fiber)
        self._slot_stream.append(slot)
        c1, c2 = self._gt_context
        bits = self._cost(c1, c2, slot)
        if c1 is not None and c2 is not None:
            inner = self._gt_counts.setdefault((c1, c2), {})
            inner[slot] = inner.get(slot, 0) + 1
        self._gt_context = (c2, slot)
        self._cum_bits += bits
        self._n_steps += 1
        return bits

    def _cost(self, c1: Optional[str], c2: Optional[str], slot: str) -> float:
        if c1 is None or c2 is None:
            return math.log2(self.alphabet_size)
        inner = self._gt_counts.get((c1, c2), {})
        total = sum(inner.values())
        p = (inner.get(slot, 0) + self.alpha) / (
            total + self.alpha * self.alphabet_size
        )
        return -math.log2(p) if p > 0 else math.log2(self.alphabet_size) * 2

    def compression_bits(self) -> float:
        return self._cum_bits

    def n_steps(self) -> int:
        return self._n_steps

    def n_contexts(self) -> int:
        return len(self._gt_counts)

    def slot_stream(self) -> List[str]:
        """The recorded V₄ slot stream. Used by the decoder follow-on to
        verify encoder/decoder symmetry once the (slot → generator → symbol)
        residual codec is added."""
        return self._slot_stream
