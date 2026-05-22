"""DD8: Substrate atlas sweep with Cl(ℝ⁸) XOR-mask layer.

For each (corpus × clifford_grade_cap) cell, measure the encoded
size and the chosen mask. Compares:
  baseline: speculate_clifford=False, no header byte for mask.
  cap=2   : restricted to bivector content (the AA-arc analog).
  cap=4   : opens grade-3 / grade-4 (cascade content).
  cap=8   : full search (255 nontrivial masks).

Per [[multi-reading-ambient-discipline]] all four readings are
reported; no single grade-cap is privileged. Per
[[negative-findings-corpus-bound]] any "no witness" outcome is
bounded by the tested grade-caps and tested corpora.

Run: `python -m tests.test_dd_arc_atlas_sweep` from `scratch/eliza`.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eliza.gpu_codec_v7 import decode, encode
from tests.test_substrate_atlas import CORPORA


SIZES = (1024, 2048)
CAPS = (None, 2, 4, 8)   # None = identity (no Clifford)


def measure(name: str, data: bytes, cap):
    t0 = time.perf_counter()
    if cap is None:
        encoded, meta = encode(data)
    else:
        encoded, meta = encode(data, speculate_clifford=True,
                                  clifford_grade_cap=cap)
    encode_ms = (time.perf_counter() - t0) * 1000
    back = decode(encoded)
    ok = back == data
    bpb = len(encoded) * 8 / max(len(data), 1)
    return bpb, meta.get("clifford_grade", 0), meta.get("clifford_mask", 0), ok, encode_ms


def main() -> int:
    print("DD8: Substrate atlas sweep with Cl(ℝ⁸) XOR-mask")
    print()
    fail = False
    for size in SIZES:
        print(f"--- size={size} bytes ---")
        print(f"{'corpus':<22} {'mode':<10} {'bpb':>7} {'mask':>5} "
              f"{'g':>2} {'ms':>6}")
        for corpus_name, builder in CORPORA.items():
            data = builder(size)
            row_results = []
            for cap in CAPS:
                bpb, g, m, ok, ms = measure(corpus_name, data, cap)
                row_results.append((cap, bpb, g, m, ok, ms))
                if not ok:
                    fail = True
            # Print rows aligned.
            for cap, bpb, g, m, ok, ms in row_results:
                cap_str = "identity" if cap is None else f"cap={cap}"
                ok_str = "" if ok else "  **FAIL**"
                print(f"{corpus_name:<22} {cap_str:<10} {bpb:>7.3f} "
                      f"{m:>5} {g:>2} {ms:>6.1f}{ok_str}")
            # Compute best across non-identity caps.
            baseline = row_results[0][1]
            best_cl = min(r[1] for r in row_results[1:])
            best_cap = next(r[0] for r in row_results[1:] if r[1] == best_cl)
            delta_pct = (best_cl - baseline) / baseline * 100
            print(f"{corpus_name:<22} {'best':<10} Δ={delta_pct:+.2f}% "
                  f"@cap={best_cap}")
            print()
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
