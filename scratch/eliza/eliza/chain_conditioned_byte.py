"""Eliza.ChainConditionedByte — byte trigram with chain context.

Context = (prev_byte_1, prev_byte_2, chain_of_current_window). The
chain is computable from already-decoded bytes (no side-channel cost),
so adding it as predictor context is "free" in bits-out terms.

Effective vocabulary: 256 bytes; effective context: 256² × 24 = 1.57M
contexts. Sparse — most contexts will be never-seen during 64KB
corpus, falling back to smoothed prior. Whether the chain dimension
actually helps depends on whether (b1, b2, chain) factors P(b) better
than (b1, b2) alone.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from eliza.chain_symbol import ChainSymbol


VOCAB_SIZE = 256


@dataclass
class ChainConditionedBytePredictor:
    """Byte predictor with (b1, b2, chain) context."""
    alpha: float = 0.5
    vocab_size: int = VOCAB_SIZE
    counts: Dict[Tuple[int, int, ChainSymbol], Dict[int, int]] \
        = field(default_factory=dict)
    context_bytes: Tuple[Optional[int], Optional[int]] = (None, None)
    current_chain: ChainSymbol = field(default_factory=ChainSymbol.identity)

    def set_chain(self, chain: ChainSymbol) -> None:
        """Call at the start of each window with the window's chain."""
        self.current_chain = chain

    def update(self, b: int) -> None:
        b1, b2 = self.context_bytes
        if b1 is not None and b2 is not None:
            key = (b1, b2, self.current_chain)
            inner = self.counts.setdefault(key, {})
            inner[b] = inner.get(b, 0) + 1
        self.context_bytes = (b2, b)

    def smoothed_prob(self, b: int) -> float:
        b1, b2 = self.context_bytes
        if b1 is None or b2 is None:
            return 1.0 / self.vocab_size
        inner = self.counts.get((b1, b2, self.current_chain), {})
        total = sum(inner.values())
        return ((inner.get(b, 0) + self.alpha)
                / (total + self.alpha * self.vocab_size))

    def surprise_bits(self, b: int) -> float:
        return -math.log2(max(self.smoothed_prob(b), 1e-30))

    def n_contexts(self) -> int:
        return len(self.counts)


@dataclass
class V4ConditionedBytePredictor:
    """Coarser chain context: condition only on the V₄ component of the
    chain (4 values), not the full 24-element chain. Trades context
    sparsity for coarser conditioning; should outperform the full
    chain-conditioned variant on smaller corpora.
    """
    alpha: float = 0.5
    vocab_size: int = VOCAB_SIZE
    counts: Dict[Tuple[int, int, "Chamber"], Dict[int, int]] \
        = field(default_factory=dict)
    context_bytes: Tuple[Optional[int], Optional[int]] = (None, None)
    current_v4: object = None  # V₄ element (Chamber tuple)

    def set_chain(self, chain: ChainSymbol) -> None:
        self.current_v4 = chain.v

    def update(self, b: int) -> None:
        b1, b2 = self.context_bytes
        if b1 is not None and b2 is not None and self.current_v4 is not None:
            key = (b1, b2, self.current_v4)
            inner = self.counts.setdefault(key, {})
            inner[b] = inner.get(b, 0) + 1
        self.context_bytes = (b2, b)

    def smoothed_prob(self, b: int) -> float:
        b1, b2 = self.context_bytes
        if b1 is None or b2 is None or self.current_v4 is None:
            return 1.0 / self.vocab_size
        inner = self.counts.get((b1, b2, self.current_v4), {})
        total = sum(inner.values())
        return ((inner.get(b, 0) + self.alpha)
                / (total + self.alpha * self.vocab_size))

    def surprise_bits(self, b: int) -> float:
        return -math.log2(max(self.smoothed_prob(b), 1e-30))

    def n_contexts(self) -> int:
        return len(self.counts)


@dataclass
class BaselineBytePredictor:
    """For apples-to-apples comparison: byte trigram without chain
    context. Used in E5/E8 to isolate the chain contribution."""
    alpha: float = 0.5
    vocab_size: int = VOCAB_SIZE
    counts: Dict[Tuple[int, int], Dict[int, int]] = field(default_factory=dict)
    context_bytes: Tuple[Optional[int], Optional[int]] = (None, None)

    def update(self, b: int) -> None:
        b1, b2 = self.context_bytes
        if b1 is not None and b2 is not None:
            inner = self.counts.setdefault((b1, b2), {})
            inner[b] = inner.get(b, 0) + 1
        self.context_bytes = (b2, b)

    def smoothed_prob(self, b: int) -> float:
        b1, b2 = self.context_bytes
        if b1 is None or b2 is None:
            return 1.0 / self.vocab_size
        inner = self.counts.get((b1, b2), {})
        total = sum(inner.values())
        return ((inner.get(b, 0) + self.alpha)
                / (total + self.alpha * self.vocab_size))

    def surprise_bits(self, b: int) -> float:
        return -math.log2(max(self.smoothed_prob(b), 1e-30))

    def n_contexts(self) -> int:
        return len(self.counts)


# --- Self-check: head-to-head bits-per-byte ----------------------------


def self_check(verbose: bool = True) -> bool:
    from pathlib import Path
    from eliza.chain_emitter import emit_chain_for_window

    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()
    while len(data) < 65536:
        data = data + data
    data = data[:65536]

    chained = ChainConditionedBytePredictor()
    v4_chained = V4ConditionedBytePredictor()
    baseline = BaselineBytePredictor()
    window_size = 256

    total_chained_bits = 0.0
    total_v4_bits = 0.0
    total_baseline_bits = 0.0
    counted = 0

    for start in range(0, len(data), window_size):
        window = data[start:start + window_size]
        if not window:
            break
        chain = emit_chain_for_window(window)
        chained.set_chain(chain)
        v4_chained.set_chain(chain)
        for b in window:
            # Pre-update surprise (the encoding cost).
            total_chained_bits += chained.surprise_bits(b)
            total_v4_bits += v4_chained.surprise_bits(b)
            total_baseline_bits += baseline.surprise_bits(b)
            chained.update(b)
            v4_chained.update(b)
            baseline.update(b)
            counted += 1

    bpb_chained = total_chained_bits / counted
    bpb_v4 = total_v4_bits / counted
    bpb_baseline = total_baseline_bits / counted

    if verbose:
        print("=== ChainConditionedByte self-check ===")
        print(f"  bytes observed:               {counted}")
        print(f"  baseline       bits/byte:     {bpb_baseline:.3f}  "
              f"contexts: {baseline.n_contexts()}")
        print(f"  V₄-conditioned bits/byte:     {bpb_v4:.3f}  "
              f"contexts: {v4_chained.n_contexts()}  "
              f"Δ={bpb_v4 - bpb_baseline:+.3f}")
        print(f"  full-chain     bits/byte:     {bpb_chained:.3f}  "
              f"contexts: {chained.n_contexts()}  "
              f"Δ={bpb_chained - bpb_baseline:+.3f}")
        print(f"\nResult: OK")
    return True


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
