"""JJ2-JJ7: Saturation curve across Sylow-prime subsets.

For each substrate corpus, measure I(chain; joint_atlas) as we
include progressively more Sylow primes:
  Single-Sylow:    {2}, {3}, {5}, {7}, {11}, {13}
  Pair:            {2,3}, {2,5}, ..., {7,11}, ...
  Triple:          {2,3,5}, {2,3,7}, ..., {5,7,11}, ...
  Quad:            {2,3,5,7}, ..., {3,5,7,11}, ...
  Quint:           {2,3,5,7,11}, ...
  Sext:            {2,3,5,7,11,13}

Track diminishing returns; identify the saturation point.

Per [[multi-route-equivariance-recovery]]: cross-Sylow combination
generates the full gauge group; the joint atlas's MI should grow
until reaching H(chain) saturation.
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.prime_chain import mutual_information
from eliza.sylow_prime_probe import all_subsets, joint_sylow_context
from tests.test_hh_arc_past_chain_mi import chain_symbols
from tests.test_substrate_atlas import CORPORA


def measure_subset(chain: np.ndarray, subset: tuple) -> float:
    ctx = joint_sylow_context(chain, subset)
    _, _, mi = mutual_information(chain, ctx, 24)
    return mi


def saturation_curve(chain: np.ndarray, primes: list) -> dict:
    """Returns {size: best subset MI of that size}."""
    subsets = all_subsets(primes)
    best_per_size = {}
    for sub in subsets:
        mi = measure_subset(chain, sub)
        size = len(sub)
        if size not in best_per_size or mi > best_per_size[size][1]:
            best_per_size[size] = (sub, mi)
    return best_per_size


def main() -> int:
    primes_gl4 = [2, 3, 5, 7]
    primes_extended = [2, 3, 5, 7, 11, 13]

    print("JJ saturation curve — best joint MI per |Sylow-subset|")
    print()
    print("Primary set: {2, 3, 5, 7} (GL(4, F₂) Sylow primes)")
    print()
    for size in (2048, 8192):
        print(f"--- size={size} bytes ---")
        print(f"{'corpus':<22} {'H(c)':>5} {'|S|=1':>9} {'|S|=2':>9} "
              f"{'|S|=3':>10} {'|S|=4':>10}")
        for name, builder in CORPORA.items():
            data = builder(size)
            chain = chain_symbols(data)
            h_chain = mutual_information(chain, chain, 24)[0]
            curve = saturation_curve(chain, primes_gl4)
            row = f"{name:<22} {h_chain:>5.2f}"
            for sz in (1, 2, 3, 4):
                sub, mi = curve[sz]
                ratio = mi / h_chain if h_chain > 0 else 0.0
                sub_str = str(sub)
                row += f"  {sub_str:>4}={mi:>4.2f}"
            print(row)
        print()

    print()
    print("Extended set: {2, 3, 5, 7, 11, 13} (small Sylow primes)")
    print("(8KB only; |S|=6 needs sample size)")
    print()
    for size in (8192,):
        print(f"--- size={size} bytes ---")
        print(f"{'corpus':<22} {'H(c)':>5} {'|S|=1':>9} {'|S|=2':>9} "
              f"{'|S|=3':>9} {'|S|=4':>9} {'|S|=5':>10} {'|S|=6':>10}")
        for name, builder in CORPORA.items():
            data = builder(size)
            chain = chain_symbols(data)
            h_chain = mutual_information(chain, chain, 24)[0]
            curve = saturation_curve(chain, primes_extended)
            row = f"{name:<22} {h_chain:>5.2f}"
            for sz in (1, 2, 3, 4, 5, 6):
                sub, mi = curve[sz]
                row += f"  s={sz}={mi:>4.2f}"
            print(row)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
