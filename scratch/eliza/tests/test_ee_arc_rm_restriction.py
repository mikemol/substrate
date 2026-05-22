"""EE2: RM(1,3) restriction baseline measurement.

Compare codec compression with:
  (a) DD-arc unrestricted cap=8 sweep (256 masks, RM(3,3))
  (b) cap=8 restricted to RM(2, 3)'s 128 even-weight codewords
  (c) cap=8 restricted to RM(1, 3)'s 16 affine codewords

Quantifies how much structure lives in RM(r+1, 3) \\ RM(r, 3) layer.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.clifford_tracer import (
    apply_clifford_mask, find_best_clifford_mask,
    find_best_clifford_mask_in_set, mask_grade,
)
from eliza.gpu_codec_v7 import decode, encode
from eliza.reed_muller import all_codewords
from tests.test_substrate_atlas import CORPORA


def encode_with_mask(data: bytes, mask: int):
    return encode(data, clifford_mask=mask)


def measure_at_restriction(data: bytes, restriction: str):
    if restriction == "RM(3,3)":
        # Full DD-arc sweep.
        mask, _ = find_best_clifford_mask(data, grade_cap=8)
    elif restriction == "RM(2,3)":
        cws = all_codewords(3, 2)
        mask, _ = find_best_clifford_mask_in_set(data, cws)
    elif restriction == "RM(1,3)":
        cws = all_codewords(3, 1)
        mask, _ = find_best_clifford_mask_in_set(data, cws)
    elif restriction == "RM(0,3)":
        mask, _ = find_best_clifford_mask_in_set(data, [0, 0xFF])
    else:
        raise ValueError(restriction)
    encoded, meta = encode_with_mask(data, mask)
    back = decode(encoded)
    bpb = len(encoded) * 8 / max(len(data), 1)
    return mask, mask_grade(mask), bpb, back == data


def main() -> int:
    print("EE2: RM(r, 3) restriction baseline")
    print()
    restrictions = ("RM(0,3)", "RM(1,3)", "RM(2,3)", "RM(3,3)")
    size = 2048
    fail = False
    for corpus_name, builder in CORPORA.items():
        data = builder(size)
        print(f"--- {corpus_name} ({size} B) ---")
        print(f"{'restriction':<12} {'mask':>5} {'g':>2} {'bpb':>7} ok")
        baseline = None
        for restriction in restrictions:
            mask, g, bpb, ok = measure_at_restriction(data, restriction)
            if not ok:
                fail = True
            note = ""
            if baseline is None:
                baseline = bpb
            else:
                delta = (bpb - baseline) / baseline * 100
                note = f"  Δ={delta:+.2f}% vs RM(0,3)"
            print(f"{restriction:<12} {mask:>5} {g:>2} {bpb:>7.3f} "
                  f"{'OK' if ok else 'FAIL'}{note}")
        print()
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
