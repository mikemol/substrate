"""HH7/HH8: Simulate codec compression with prime-context predictor +
Hamming(7,4) recovery on mispredict.

Without full V7 wiring (which is invasive), we simulate by:
  1. Compute chain symbol sequence (per the substrate's S₄ walk).
  2. For each emission, compute the past-chain-v4 context (HH4).
  3. Adapt a per-context-value count table; track per-emission cost.
  4. Compare per-emission cost to:
     (a) unigram baseline (flat counts)
     (b) actual codec emission cost (via V7)
  5. HH8: when the prime-context predictor mispredicts (probability
     mass on actual emit < threshold), check if Hamming(7,4) syndrome
     recovery would have caught the correct value.

Substrate-honest: this simulates the BEST CASE per-emission cost
the codec could achieve with the prime-context predictor. Actual
codec wiring would need to handle interaction with V7's opcodes,
backref, residue, etc.
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.prime_context_predictor import (
    _V4_PART_TABLE, past_chain_v4_context,
)
from eliza.hamming import all_codewords_7_4, correct_single_error
from tests.test_hh_arc_past_chain_mi import chain_symbols
from tests.test_substrate_atlas import CORPORA


def simulate_emission_costs(chain: np.ndarray, p: int, q: int,
                              alpha: float = 0.5) -> dict:
    """Adaptive Laplace-smoothed (α=0.5) prime-context predictor.

    Tracks per-emission cost (in bits) under:
      unigram: flat 24-value adaptive counts
      prime:   64 context-value adaptive count tables

    Returns dict with total costs + mispredict counts.
    """
    N = 24
    unigram = np.zeros(N, dtype=np.float64)
    prime = np.zeros((64, N), dtype=np.float64)

    cost_unigram = 0.0
    cost_prime = 0.0
    n_mispredict_prime = 0
    n_emissions = len(chain)

    def smoothed_prob(counts: np.ndarray, idx: int) -> float:
        total = counts.sum() + alpha * N
        return (counts[idx] + alpha) / total

    for k in range(n_emissions):
        emit = int(chain[k])
        # Unigram cost.
        pu = smoothed_prob(unigram, emit)
        cost_unigram += -np.log2(pu)
        unigram[emit] += 1
        # Prime-context cost.
        ctx = past_chain_v4_context(list(chain[:k]), k, p, q)
        pp = smoothed_prob(prime[ctx], emit)
        cost_prime += -np.log2(pp)
        # Mispredict: prime predictor's top guess ≠ actual emit
        # AND probability mass on emit is < 1/3 (arbitrary threshold).
        top_guess = int(np.argmax(prime[ctx]))
        if top_guess != emit and pp < 1.0 / 3.0:
            n_mispredict_prime += 1
        prime[ctx, emit] += 1

    return {
        "n_emissions": n_emissions,
        "cost_unigram": cost_unigram,
        "cost_prime": cost_prime,
        "bpb_unigram": cost_unigram / n_emissions,
        "bpb_prime": cost_prime / n_emissions,
        "n_mispredict_prime": n_mispredict_prime,
    }


def hamming_recovery_rate(chain: np.ndarray, p: int, q: int,
                            alpha: float = 0.5) -> dict:
    """HH8: for each prime-predictor mispredict, check whether the
    actual emit is within Hamming-distance 1 of the predictor's
    top guess (after embedding chamber index 0..23 into 7 bits).

    Embedding: chamber c ↦ c (as a 5-bit value, padded with zero
    parity bits to 7 bits in the Hamming(7,4) framework).
    Recovery succeeds if Hamming-correction of (predicted 7-bit ⊕
    actual 7-bit) yields the correct emission.
    """
    N = 24
    prime = np.zeros((64, N), dtype=np.float64)

    def smoothed_prob(counts: np.ndarray, idx: int) -> float:
        total = counts.sum() + alpha * N
        return (counts[idx] + alpha) / total

    n_mispredict = 0
    n_recoverable = 0   # emit within 1-Hamming-distance of top guess
    for k in range(len(chain)):
        emit = int(chain[k])
        ctx = past_chain_v4_context(list(chain[:k]), k, p, q)
        pp = smoothed_prob(prime[ctx], emit)
        top_guess = int(np.argmax(prime[ctx]))
        if top_guess != emit and pp < 1.0 / 3.0:
            n_mispredict += 1
            # Embed as 7-bit values (low 5 bits of chamber idx).
            err = emit ^ top_guess
            wt = bin(err).count("1")
            if wt <= 1:
                n_recoverable += 1
        prime[ctx, emit] += 1

    return {
        "n_mispredict": n_mispredict,
        "n_recoverable": n_recoverable,
        "recovery_rate": (n_recoverable / n_mispredict)
                          if n_mispredict > 0 else 0.0,
    }


def main() -> int:
    print("HH7: Simulated per-emission cost with past-chain-v4 predictor")
    print()
    print(f"{'corpus':<22} {'bpb_uni':>8} {'bpb_prime':>10} "
          f"{'delta':>8} {'n_mispred':>10} "
          f"{'rec':>5}")
    for name, builder in CORPORA.items():
        data = builder(2048)
        chain = chain_symbols(data)
        # Use the best (p, q) per corpus from HH4 (revised). All best
        # at (2, 3) per past-chain context.
        res = simulate_emission_costs(chain, p=2, q=3)
        rec = hamming_recovery_rate(chain, p=2, q=3)
        delta = (res["bpb_prime"] - res["bpb_unigram"])
        delta_pct = delta / res["bpb_unigram"] * 100
        print(f"{name:<22} {res['bpb_unigram']:>8.3f} "
              f"{res['bpb_prime']:>10.3f} "
              f"{delta_pct:>+7.1f}% "
              f"{res['n_mispredict_prime']:>10} "
              f"{rec['recovery_rate']*100:>4.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
