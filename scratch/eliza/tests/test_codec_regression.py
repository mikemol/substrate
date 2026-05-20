"""tests/test_codec_regression.py — T7+T8 performance + correctness suite.

Locked-in regression check for V2 / V4 / V5 against L0 CPU baseline.
Covers sizes 1KB / 2KB / 4KB / 8KB / 16KB and corpora text / elf /
zeros.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from eliza.adaptive_opcode_codec import encode as l0_enc, decode as l0_dec
from eliza.gpu_codec_v2 import encode as v2_enc, decode as v2_dec
from eliza.gpu_codec_v4 import encode as v4_enc, decode as v4_dec
from eliza.gpu_codec_v5 import encode as v5_enc, decode as v5_dec


def _text(n):
    src = ROOT / "eliza" / "engine.py"
    with open(src, "rb") as f:
        d = f.read()
    while len(d) < n:
        d = d + d
    return d[:n]


def _elf(n):
    with open("/bin/true", "rb") as f:
        return f.read(n)


def _zeros(n):
    return b"\x00" * n


CORPORA = {"text": _text, "elf": _elf, "zeros": _zeros}
SIZES = (1024, 2048, 4096, 8192)


def main() -> int:
    print("=== T8: full regression suite (L0 / V2 / V4 / V5) ===\n")
    print(f"{'corpus':>8} {'size':>5}  {'L0 b/byte':>10}  {'V2 b/byte':>10}  "
          f"{'V4 b/byte':>10}  {'V5 b/byte':>10}  {'L0 time':>9}  "
          f"{'V2 time':>9}  {'V5 time':>9}  {'V5/L0':>7}")
    all_ok = True

    for size in SIZES:
        for name, factory in CORPORA.items():
            d = factory(size)

            t0 = time.perf_counter()
            el, _ = l0_enc(d); dl = l0_dec(el)
            t_l = time.perf_counter() - t0
            bl = 8*len(el)/len(d)
            ok_l = dl == d

            t0 = time.perf_counter()
            e2, _ = v2_enc(d); d2 = v2_dec(e2)
            t_2 = time.perf_counter() - t0
            b2 = 8*len(e2)/len(d)
            ok_2 = d2 == d

            t0 = time.perf_counter()
            e4, _ = v4_enc(d); d4 = v4_dec(e4)
            t_4 = time.perf_counter() - t0
            b4 = 8*len(e4)/len(d)
            ok_4 = d4 == d

            t0 = time.perf_counter()
            e5, _ = v5_enc(d); d5 = v5_dec(e5)
            t_5 = time.perf_counter() - t0
            b5 = 8*len(e5)/len(d)
            ok_5 = d5 == d

            iter_ok = ok_l and ok_2 and ok_4 and ok_5
            all_ok = all_ok and iter_ok

            ratio = t_5/t_l if t_l > 0 else float('inf')
            print(f"{name:>8} {size:>5}  {bl:>10.3f}  {b2:>10.3f}  "
                  f"{b4:>10.3f}  {b5:>10.3f}  {t_l*1000:>7.1f}ms  "
                  f"{t_2*1000:>7.1f}ms  {t_5*1000:>7.1f}ms  {ratio:>6.2f}x"
                  f"  {'OK' if iter_ok else 'FAIL'}")

    print(f"\n=== Result: {'OK' if all_ok else 'FAIL'} ===")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
