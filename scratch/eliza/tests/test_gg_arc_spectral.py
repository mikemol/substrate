"""GG7: Spectral feature × compression-ratio correlation.

For each corpus × size, measure:
  spectral atlas features (entropy_p, sparsity_p, cross_prime_pq)
  codec compression bpb (under multiple modes)

Look for spectral features that predict compression difficulty.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import numpy as np

from eliza.gpu_codec_v7 import encode
from eliza.spectral_atlas import spectral_atlas
from eliza.spectral_predictor import classify_spectrum
from tests.test_substrate_atlas import CORPORA


def main() -> int:
    print("GG7: Spectral features × codec compression")
    print()
    rows = []
    sizes = (1024, 2048)
    for size in sizes:
        for name, builder in CORPORA.items():
            data = builder(size)
            atlas = spectral_atlas(data)
            cls = classify_spectrum(data)
            # Pure baseline + DD-arc cap=8 + AA-arc backref full stack.
            enc_id, _ = encode(data)
            enc_dd, _ = encode(data, speculate_clifford=True,
                                  clifford_grade_cap=8)
            enc_full, _ = encode(data, speculate_clifford=True,
                                    clifford_grade_cap=8,
                                    speculate_backref=True,
                                    speculate_s4_residue=True)
            row = {
                "corpus": name,
                "size": size,
                "class": cls,
                "H_p2": atlas["entropy"][2],
                "H_p3": atlas["entropy"][3],
                "H_p5": atlas["entropy"][5],
                "H_p7": atlas["entropy"][7],
                "sparsity_p7": atlas["sparsity"][7],
                "M_27": atlas["cross_prime"][0, 3],
                "M_37": atlas["cross_prime"][1, 3],
                "M_57": atlas["cross_prime"][2, 3],
                "bpb_id": len(enc_id) * 8 / size,
                "bpb_dd": len(enc_dd) * 8 / size,
                "bpb_full": len(enc_full) * 8 / size,
            }
            rows.append(row)

    print(f"{'corpus':<22} {'size':>5} {'cls':>3} {'H7':>5} "
          f"{'sp7':>5} {'M27':>5} {'M37':>5} {'M57':>5} "
          f"{'id':>5} {'dd':>5} {'full':>5}")
    for r in rows:
        print(f"{r['corpus']:<22} {r['size']:>5} {r['class']:>3} "
              f"{r['H_p7']:>5.2f} {r['sparsity_p7']:>5.3f} "
              f"{r['M_27']:>+5.2f} {r['M_37']:>+5.2f} {r['M_57']:>+5.2f} "
              f"{r['bpb_id']:>5.2f} {r['bpb_dd']:>5.2f} "
              f"{r['bpb_full']:>5.2f}")

    # Pearson correlation: spectral features vs compression ratios.
    print()
    print("Pearson correlations (across all measurements):")
    bpb_full = np.array([r["bpb_full"] for r in rows], dtype=np.float64)
    for feat in ("H_p2", "H_p3", "H_p5", "H_p7", "sparsity_p7",
                 "M_27", "M_37", "M_57"):
        x = np.array([r[feat] for r in rows], dtype=np.float64)
        # Pearson correlation.
        if x.std() == 0:
            continue
        corr = float(np.corrcoef(x, bpb_full)[0, 1])
        print(f"  {feat:<14} → bpb_full: r = {corr:+.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
