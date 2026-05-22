"""II3+II4+II5+II6: Atlas sweep across substrate atlas corpora.

For each kinematic gauge-class atlas:
  Single-atlas MI: I(chain_symbol; atlas_context)
  Pairwise joint MI: I(chain; A_i ⊗ A_j) for all (i, j) pairs

Identify supra-additive pairs (joint > sum of marginals) which
indicate synergistic Sylow-class combinations per
[[multi-route-equivariance-recovery]].

Per the user 2026-05-21: 'combinatorial dot product, so we can find
which permutations work best with each other'.
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.prime_chain import mutual_information
from eliza.probe_atlas import (
    ATLAS_REGISTRY, atlas_context_stream, joint_atlas_context_stream,
)
from tests.test_hh_arc_past_chain_mi import chain_symbols
from tests.test_substrate_atlas import CORPORA


def single_atlas_mi(chain: np.ndarray, p: int = 2, q: int = 3) -> dict:
    """Return {atlas_name: MI(chain; atlas_context)}."""
    h_chain = mutual_information(chain, chain, 24)[0]
    out = {}
    for atlas in ATLAS_REGISTRY:
        ctx = atlas_context_stream(chain, atlas, p, q)
        _, _, mi = mutual_information(chain, ctx, 24)
        out[atlas.name] = (mi, mi / h_chain if h_chain > 0 else 0.0)
    return out


def pairwise_joint_mi(chain: np.ndarray, p: int = 2, q: int = 3) -> dict:
    """Return {(name_i, name_j): MI(chain; A_i ⊗ A_j)} for i < j.

    Only computes pairs where joint context size ≤ 4096 to keep MI
    estimation reliable on 2048-byte (4096 chain symbols) data.
    """
    out = {}
    for i, A in enumerate(ATLAS_REGISTRY):
        for j, B in enumerate(ATLAS_REGISTRY):
            if i >= j:
                continue
            # Combined bit-width: 2 * (probes_A + probes_B) ≤ 12.
            probes_A = len(A.offsets_fn(p, q)[:A.max_probes])
            probes_B = len(B.offsets_fn(p, q)[:B.max_probes])
            total_bits = 2 * (probes_A + probes_B)
            if total_bits > 12:
                # Skip — joint context too large.
                continue
            stream = joint_atlas_context_stream(chain, [A, B], p, q)
            _, _, mi = mutual_information(chain, stream, 24)
            out[(A.name, B.name)] = mi
    return out


def supra_additive(pairs_mi: dict, single_mi: dict) -> list:
    """Identify pairs where joint MI exceeds sum of marginals.

    Reading: MI(A ⊗ B) ≥ max(MI(A), MI(B)). The "synergy" is
    MI(A ⊗ B) - max(MI(A), MI(B)) — how much information the pair
    adds beyond the better single chart.
    """
    results = []
    for (a, b), joint_mi in pairs_mi.items():
        mi_a = single_mi[a][0]
        mi_b = single_mi[b][0]
        synergy = joint_mi - max(mi_a, mi_b)
        results.append((a, b, joint_mi, synergy))
    results.sort(key=lambda t: -t[3])
    return results


def main() -> int:
    print("II3+II4+II5+II6: Atlas-of-probes sweep")
    print()
    print("Per [[multi-route-equivariance-recovery]]: each Sylow class")
    print("contributes an atlas chart; the joint atlas carries equivariance")
    print("that no single chart can.")
    print()

    for name, builder in CORPORA.items():
        data = builder(2048)
        chain = chain_symbols(data)
        h_chain = mutual_information(chain, chain, 24)[0]
        print(f"=== {name} (2048B)  H(chain)={h_chain:.3f} ===")
        # II3: single-atlas MI.
        single = single_atlas_mi(chain)
        print("  Single-atlas MI (sorted):")
        sorted_single = sorted(single.items(), key=lambda t: -t[1][0])
        for atlas_name, (mi, ratio) in sorted_single[:5]:
            atlas = next(a for a in ATLAS_REGISTRY if a.name == atlas_name)
            print(f"    {atlas_name:<15} (S{atlas.sylow}): MI={mi:.3f}  "
                  f"({ratio*100:.1f}%)")
        print(f"    ... ({len(sorted_single) - 5} more)")

        # II4+II5: pairwise joint MI, identify top synergistic pairs.
        pairs = pairwise_joint_mi(chain)
        synergistic = supra_additive(pairs, single)
        print(f"  Pairwise joint-MI matrix: {len(pairs)} tractable pairs")
        print("  Top synergistic pairs (joint MI – max(marginal)):")
        for a, b, joint_mi, syn in synergistic[:5]:
            sa = next(x for x in ATLAS_REGISTRY if x.name == a).sylow
            sb = next(x for x in ATLAS_REGISTRY if x.name == b).sylow
            sylow_tag = f"S{sa}×S{sb}"
            print(f"    {a:<13} ⊗ {b:<13} ({sylow_tag}): "
                  f"joint={joint_mi:.3f}  synergy=+{syn:.3f} bits")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
