"""tests/test_bitshift_alignment.py — CC7: 8-alignment test methodology.

Per the user's CC-arc insight: bit-alignment is a hidden gauge at
the test methodology layer; reporting only byte-aligned readings
privileges an I/O convention without structural justification.

Each adversarial / substrate corpus is measured at all 8 stream-level
bit-shifts (Z/8 group). The report includes per-alignment bpb and
the best-alignment summary.

Per [[multi-reading-ambient-discipline]] the 8 readings together are
the structural measurement; any single alignment is one orbit-point.
Per [[3plus1-parity-universal]] the 8 = 2³ shifts realise the Z/8
group's three independent bits.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from eliza.gpu_codec_v7 import encode, decode    # noqa: E402
from tests.test_substrate_atlas import CORPORA    # noqa: E402


def main(size: int = 2048) -> int:
    print(f"=== CC7: 8-alignment sweep — {size}B per corpus ===\n")
    print(f"{'corpus':<22}" + "".join(f"{f'shift={s}':>10}"
                                          for s in range(8))
          + f"  {'best':>10}  {'gain':>8}")

    for cname, ctor in CORPORA.items():
        data = ctor(n_bytes=size)
        row = []
        for shift in range(8):
            try:
                enc, _ = encode(data, bit_shift=shift)
                dec = decode(enc)
                ok = dec == data
                bpb = 8 * len(enc) / len(data) if ok else -1.0
            except Exception:
                bpb = -1.0
                ok = False
            row.append(bpb)
        baseline = row[0]
        best = min(b for b in row if b > 0)
        gain = baseline - best
        cells = "".join(f"{v:>10.3f}" for v in row)
        print(f"{cname:<22}{cells}  {best:>10.3f}  "
              f"{gain:>+8.3f}")

    print()
    print("baseline = shift=0; best = min across 8 shifts.")
    print("Negative gain = best alignment is byte-aligned (shift=0).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
