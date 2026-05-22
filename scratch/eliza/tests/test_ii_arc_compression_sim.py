"""II7+II8: Compression simulation with best-single-atlas and best-
synergistic-pair predictors, plus Hamming(7,4) recovery on
mispredict cases.

Per [[multi-route-equivariance-recovery]]: the joint atlas carries
predictability that no single chart does. We measure this in
per-emission cost.
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.probe_atlas import (
    ATLAS_REGISTRY, atlas_context_stream, joint_atlas_context_stream,
)
from tests.test_hh_arc_past_chain_mi import chain_symbols
from tests.test_substrate_atlas import CORPORA


def atlas_by_name(name: str):
    return next(a for a in ATLAS_REGISTRY if a.name == name)


def simulate_under_predictor(
    chain: np.ndarray, context_stream: np.ndarray,
    n_emissions: int, alpha: float = 0.5,
) -> tuple:
    """Adaptive predictor over context_stream → cost in bits.

    Returns (total_cost_bits, n_mispredict, n_hamming_recoverable).
    """
    N = 24
    n_ctx = int(context_stream.max()) + 1 if len(context_stream) else 1
    counts = np.zeros((n_ctx, N), dtype=np.float64)

    cost = 0.0
    n_mispredict = 0
    n_recoverable = 0
    for k in range(min(len(chain), len(context_stream), n_emissions)):
        emit = int(chain[k])
        ctx = int(context_stream[k])
        total = counts[ctx].sum() + alpha * N
        p_emit = (counts[ctx, emit] + alpha) / total
        cost += -np.log2(p_emit)
        top_guess = int(np.argmax(counts[ctx]))
        if top_guess != emit and p_emit < 1.0 / 3.0:
            n_mispredict += 1
            # Hamming-distance check on chamber-index XOR.
            wt = bin(emit ^ top_guess).count("1")
            if wt <= 1:
                n_recoverable += 1
        counts[ctx, emit] += 1
    return cost, n_mispredict, n_recoverable


def simulate_unigram(chain: np.ndarray, alpha: float = 0.5) -> float:
    """Unigram-only baseline cost in bits."""
    N = 24
    counts = np.zeros(N, dtype=np.float64)
    cost = 0.0
    for k in range(len(chain)):
        emit = int(chain[k])
        total = counts.sum() + alpha * N
        p = (counts[emit] + alpha) / total
        cost += -np.log2(p)
        counts[emit] += 1
    return cost


def main() -> int:
    print("II7+II8: Compression simulation + Hamming recovery")
    print()
    # Best single atlas: Rzeppa-class (6-probe linear).
    # Best synergistic pairs found per corpus.
    pairs_per_corpus = {
        "substrate_agda":     ("Thompson", "Tripod"),       # S2×S3
        "substrate_memory":   ("Cardan",   "CrossGroove"),  # S2×S7 (+1.242)
        "substrate_opcodes":  ("Thompson", "Tripod"),       # S2×S3 (+0.057)
        "t1t2_handcrafted":   ("Thompson", "Tripod"),       # S2×S3 (+0.440)
    }

    print(f"{'corpus':<22} {'bpb_uni':>8} {'bpb_Rze':>8} "
          f"{'pair_atlas':<28} {'bpb_pair':>8} {'mispred':>8} "
          f"{'recov%':>6}")
    for name, builder in CORPORA.items():
        data = builder(2048)
        chain = chain_symbols(data)
        n_emit = len(chain)

        # Unigram baseline.
        cost_uni = simulate_unigram(chain)

        # Single-atlas (Rzeppa).
        rzeppa = atlas_by_name("Rzeppa")
        ctx_rz = atlas_context_stream(chain, rzeppa, p=2, q=3)
        cost_rz, _, _ = simulate_under_predictor(chain, ctx_rz, n_emit)

        # Pair-atlas (per-corpus best).
        a_name, b_name = pairs_per_corpus[name]
        A = atlas_by_name(a_name)
        B = atlas_by_name(b_name)
        ctx_pair = joint_atlas_context_stream(chain, [A, B], p=2, q=3)
        cost_pair, n_mp, n_rec = simulate_under_predictor(
            chain, ctx_pair, n_emit)

        bpb_uni = cost_uni / n_emit
        bpb_rz = cost_rz / n_emit
        bpb_pair = cost_pair / n_emit
        pair_str = f"{a_name}⊗{b_name}"[:28]
        recov_pct = (n_rec / n_mp * 100) if n_mp > 0 else 0.0
        print(f"{name:<22} {bpb_uni:>8.3f} {bpb_rz:>8.3f} "
              f"{pair_str:<28} {bpb_pair:>8.3f} {n_mp:>8d} "
              f"{recov_pct:>5.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
