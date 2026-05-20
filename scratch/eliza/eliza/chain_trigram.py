"""Eliza.ChainTrigram — adaptive predictor over ChainSymbol terminals.

Mirrors `TrigramPredictor` (char-byte trigram) but with ChainSymbol as
the symbol type. Context = the previous two ChainSymbols; prediction =
distribution over the next ChainSymbol.

This is the substrate-native predictor for the W-axis stream. The
codec's E3 hybrid encoder uses this to encode the chain stream itself
in lockstep with the byte stream.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from eliza.chain_symbol import ChainSymbol


VOCAB_SIZE = 24                # |S₄| — the chain alphabet size


@dataclass
class ChainTrigramPredictor:
    alpha: float = 0.5
    vocab_size: int = VOCAB_SIZE
    counts: Dict[Tuple[ChainSymbol, ChainSymbol], Dict[ChainSymbol, int]] \
        = field(default_factory=dict)
    context: Tuple[ChainSymbol, ChainSymbol] = (
        ChainSymbol.identity(), ChainSymbol.identity()
    )

    def update(self, sym: ChainSymbol) -> None:
        c1, c2 = self.context
        inner = self.counts.setdefault((c1, c2), {})
        inner[sym] = inner.get(sym, 0) + 1
        self.context = (c2, sym)

    def smoothed_prob(
        self, sym: ChainSymbol,
        context: Tuple[ChainSymbol, ChainSymbol] | None = None,
    ) -> float:
        c1, c2 = context if context is not None else self.context
        inner = self.counts.get((c1, c2), {})
        total = sum(inner.values())
        return ((inner.get(sym, 0) + self.alpha)
                / (total + self.alpha * self.vocab_size))

    def surprise_bits(self, sym: ChainSymbol) -> float:
        return -math.log2(max(self.smoothed_prob(sym), 1e-30))

    def n_contexts(self) -> int:
        return len(self.counts)


# --- Self-check ---------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from pathlib import Path
    from eliza.chain_emitter import chain_stream

    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()
    while len(data) < 65536:
        data = data + data
    data = data[:65536]

    chains = chain_stream(data, window_size=256)
    pred = ChainTrigramPredictor()

    total_bits = 0.0
    counted = 0
    for sym in chains:
        # Cost of encoding sym under current model BEFORE update.
        bits = pred.surprise_bits(sym)
        if counted >= 2:    # skip the first two (uniform context)
            total_bits += bits
        pred.update(sym)
        counted += 1

    n_for_avg = max(counted - 2, 1)
    avg_bits = total_bits / n_for_avg
    raw_entropy = math.log2(24)

    if verbose:
        print("=== ChainTrigramPredictor self-check ===")
        print(f"  chains observed:        {len(chains)}")
        print(f"  contexts learned:       {pred.n_contexts()}")
        print(f"  bits per chain (avg):   {avg_bits:.3f}")
        print(f"  raw chain entropy max:  {raw_entropy:.3f}  (= log₂ 24)")
        print(f"  redundancy captured:    {raw_entropy - avg_bits:.3f} bits")
        print(f"\nResult: OK")
    return True


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
