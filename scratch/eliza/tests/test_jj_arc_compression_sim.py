"""JJ8: Compression simulation with multi-Sylow joint-context predictor.

Compare per-emission cost under predictors keyed on:
  unigram baseline
  pair-Sylow joint {2, 3}
  triple-Sylow joint {2, 3, 5}
  quad-Sylow joint {2, 3, 5, 7}
  sext-Sylow joint {2, 3, 5, 7, 11, 13}
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.sylow_prime_probe import joint_sylow_context
from tests.test_hh_arc_past_chain_mi import chain_symbols
from tests.test_substrate_atlas import CORPORA


def simulate_predictor(chain: np.ndarray, ctx_stream: np.ndarray,
                         alpha: float = 0.5) -> tuple:
    N = 24
    n_ctx = int(ctx_stream.max()) + 1 if len(ctx_stream) else 1
    counts = np.zeros((n_ctx, N), dtype=np.float64)
    cost = 0.0
    n_mispredict = 0
    n_recoverable = 0
    for k in range(min(len(chain), len(ctx_stream))):
        emit = int(chain[k])
        ctx = int(ctx_stream[k])
        total = counts[ctx].sum() + alpha * N
        p = (counts[ctx, emit] + alpha) / total
        cost += -np.log2(p)
        top_guess = int(np.argmax(counts[ctx]))
        if top_guess != emit and p < 1.0 / 3.0:
            n_mispredict += 1
            if bin(emit ^ top_guess).count("1") <= 1:
                n_recoverable += 1
        counts[ctx, emit] += 1
    return cost, n_mispredict, n_recoverable


def simulate_unigram(chain: np.ndarray, alpha: float = 0.5) -> float:
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
    print("JJ8: Compression simulation per Sylow-set composition (8KB)")
    print()
    configs = [
        ("baseline",   None),
        ("{2,3}",      [2, 3]),
        ("{2,3,5}",    [2, 3, 5]),
        ("{2,3,5,7}",  [2, 3, 5, 7]),
        ("{2,3,5,7,11}",   [2, 3, 5, 7, 11]),
        ("{2,3,5,7,11,13}",[2, 3, 5, 7, 11, 13]),
    ]
    print(f"{'corpus':<22} {'baseline':>9} {'{2,3}':>9} "
          f"{'{2,3,5}':>9} {'{2-7}':>9} {'{2-11}':>9} {'{2-13}':>9}")
    for name, builder in CORPORA.items():
        data = builder(8192)
        chain = chain_symbols(data)
        n_emit = len(chain)
        bpb_values = []
        for label, primes in configs:
            if primes is None:
                cost = simulate_unigram(chain)
            else:
                ctx = joint_sylow_context(chain, primes)
                cost, _, _ = simulate_predictor(chain, ctx)
            bpb_values.append(cost / n_emit)
        row = f"{name:<22}" + "".join(f"{v:>9.3f}" for v in bpb_values)
        print(row)
    print()
    print("Delta vs baseline (negative = better):")
    print(f"{'corpus':<22} {'{2,3}':>9} {'{2,3,5}':>9} "
          f"{'{2-7}':>9} {'{2-11}':>9} {'{2-13}':>9}")
    for name, builder in CORPORA.items():
        data = builder(8192)
        chain = chain_symbols(data)
        n_emit = len(chain)
        base = simulate_unigram(chain) / n_emit
        deltas = []
        for label, primes in configs[1:]:
            ctx = joint_sylow_context(chain, primes)
            cost, _, _ = simulate_predictor(chain, ctx)
            deltas.append((cost / n_emit - base) / base * 100)
        row = f"{name:<22}" + "".join(f"{d:>+8.1f}%" for d in deltas)
        print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
