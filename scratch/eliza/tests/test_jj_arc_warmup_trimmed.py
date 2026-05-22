"""JJ follow-up: warmup-trimmed Sylow saturation.

Per user 2026-05-21: the chain walk has a sharp transition at
position 0 (no history). Prime-offset probes zero-pad for any
offset ≥ k, producing Gibbs-phenomenon ringing in the early portion
of the predictor's adaptation. Skip the first max(primes) positions
where probes aren't fully populated and re-measure.

If the substrate_memory regression at |S|≥3 disappears after
trimming, the regression was indeed warmup ringing.
If it persists, there's a deeper sample-size issue.
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.prime_chain import mutual_information
from eliza.sylow_prime_probe import joint_sylow_context
from tests.test_hh_arc_past_chain_mi import chain_symbols
from tests.test_substrate_atlas import CORPORA


def measure_trimmed(chain: np.ndarray, primes: list,
                      warmup: int = None) -> tuple:
    """Returns (untrimmed_MI, trimmed_MI) for the given Sylow subset."""
    ctx = joint_sylow_context(chain, primes)
    _, _, mi_untrimmed = mutual_information(chain, ctx, 24)
    if warmup is None:
        warmup = max(primes)
    trimmed_chain = chain[warmup:]
    trimmed_ctx = ctx[warmup:]
    _, _, mi_trimmed = mutual_information(trimmed_chain, trimmed_ctx, 24)
    return (mi_untrimmed, mi_trimmed)


def main() -> int:
    print("JJ follow-up: warmup-trimmed Sylow saturation")
    print()
    print("Hypothesis: the substrate_memory regression at |S|≥3 is")
    print("Gibbs-phenomenon ringing from zero-padded early probes.")
    print("Trimming the first max(primes) positions should clean it up.")
    print()

    sets = [
        (2, [2, 3]),
        (3, [2, 3, 5]),
        (4, [2, 3, 5, 7]),
        (5, [2, 3, 5, 7, 11]),
        (6, [2, 3, 5, 7, 11, 13]),
    ]

    print("MI per |S| (untrimmed → trimmed), 8KB data:")
    print(f"{'corpus':<22} {'|S|=2':>15} {'|S|=3':>15} "
          f"{'|S|=4':>15} {'|S|=5':>15} {'|S|=6':>15}")
    for name, builder in CORPORA.items():
        data = builder(8192)
        chain = chain_symbols(data)
        row = f"{name:<22}"
        for sz, primes in sets:
            untrim, trim = measure_trimmed(chain, primes)
            delta_pct = (trim - untrim) / untrim * 100 if untrim > 0 else 0
            row += f"  {untrim:.2f}→{trim:.2f}({delta_pct:+.1f}%)"
        print(row)

    print()
    print("Compression simulation, warmup-trimmed (8KB):")
    print(f"{'corpus':<22} {'bpb_uni':>9} {'bpb_{2-7}':>10} "
          f"{'bpb_{2-13}':>11}  trimmed")
    for name, builder in CORPORA.items():
        data = builder(8192)
        chain = chain_symbols(data)
        from tests.test_jj_arc_compression_sim import (
            simulate_predictor, simulate_unigram,
        )
        # Untrimmed.
        cost_uni = simulate_unigram(chain) / len(chain)
        ctx7 = joint_sylow_context(chain, [2, 3, 5, 7])
        c7, _, _ = simulate_predictor(chain, ctx7)
        ctx13 = joint_sylow_context(chain, [2, 3, 5, 7, 11, 13])
        c13, _, _ = simulate_predictor(chain, ctx13)
        bpb7_u = c7 / len(chain)
        bpb13_u = c13 / len(chain)
        # Trimmed: skip warmup.
        warmup = 13
        chain_t = chain[warmup:]
        cost_uni_t = simulate_unigram(chain_t) / len(chain_t)
        ctx7_t = joint_sylow_context(chain, [2, 3, 5, 7])[warmup:]
        c7_t, _, _ = simulate_predictor(chain_t, ctx7_t)
        ctx13_t = joint_sylow_context(chain, [2, 3, 5, 7, 11, 13])[warmup:]
        c13_t, _, _ = simulate_predictor(chain_t, ctx13_t)
        bpb7_t = c7_t / len(chain_t)
        bpb13_t = c13_t / len(chain_t)
        print(f"{name:<22} {cost_uni:>9.3f} {bpb7_u:>10.3f} "
              f"{bpb13_u:>11.3f}  (untrimmed)")
        print(f"{'':<22} {cost_uni_t:>9.3f} {bpb7_t:>10.3f} "
              f"{bpb13_t:>11.3f}  (trimmed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
