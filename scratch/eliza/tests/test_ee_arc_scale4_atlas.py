"""EE5: Scale-4 RM(2, 4) word-mask atlas measurement.

Verifies (EE-E1): ∃ corpus where scale-4 RM(2, 4) strictly outperforms
scale-3 saturated DD-arc.

For each corpus × size, measures:
  (a) baseline: no Clifford, no word mask.
  (b) DD-arc:   speculate_clifford=True cap=8.
  (c) EE-arc:   speculate_word_mask=True (RM(2, 4)).
  (d) compose:  both DD-arc and EE-arc speculation.
"""

from __future__ import annotations

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.gpu_codec_v7 import decode, encode
from tests.test_substrate_atlas import CORPORA


SIZES = (1024, 2048)


def measure(data: bytes, mode_kwargs: dict):
    t0 = time.perf_counter()
    encoded, meta = encode(data, **mode_kwargs)
    ms = (time.perf_counter() - t0) * 1000
    back = decode(encoded)
    return {
        "bpb": len(encoded) * 8 / max(len(data), 1),
        "clifford": meta.get("clifford_mask", 0),
        "word": meta.get("word_mask", 0),
        "ok": back == data,
        "ms": ms,
    }


def main() -> int:
    print("EE5: Scale-4 RM(2, 4) atlas measurement")
    print()
    modes = [
        ("baseline", {}),
        ("DD cap=8", {"speculate_clifford": True, "clifford_grade_cap": 8}),
        ("EE word",  {"speculate_word_mask": True}),
        ("DD + EE",  {"speculate_clifford": True, "clifford_grade_cap": 8,
                       "speculate_word_mask": True}),
    ]
    fail = False
    for size in SIZES:
        print(f"--- size={size} bytes ---")
        print(f"{'corpus':<22} {'mode':<10} {'bpb':>7} "
              f"{'mask8':>5} {'mask16':>7} {'ms':>7}")
        for corpus_name, builder in CORPORA.items():
            data = builder(size)
            for mode_label, kw in modes:
                r = measure(data, kw)
                if not r["ok"]:
                    fail = True
                fail_tag = "  FAIL" if not r["ok"] else ""
                print(f"{corpus_name:<22} {mode_label:<10} {r['bpb']:>7.3f} "
                      f"{r['clifford']:>5} 0x{r['word']:>04x} "
                      f"{r['ms']:>7.0f}{fail_tag}")
            print()
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
