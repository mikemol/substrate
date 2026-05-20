"""tests/test_cap_sweep.py — sweep max_opcodes cap to find the regression boundary.

Hypothesis: higher cap → less compression loss from freeze, but more
match-tensor recomputes + larger alphabet → encode-time regression.

Sweep cap ∈ {128, 256, 512, 1024, 2048, 4096, 8192} on text at 4KB / 8KB / 16KB.
Report round-trip correctness, compression, encode/decode time, and
actual n_used (does the cap get hit?).
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


def text(n: int) -> bytes:
    src = ROOT / "eliza" / "engine.py"
    with open(src, "rb") as f:
        d = f.read()
    while len(d) < n:
        d = d + d
    return d[:n]


def main() -> int:
    print("=== Cap-sweep regression test (V2 on text) ===\n")
    print(f"{'size':>5} {'cap':>5}  {'V2 b/byte':>10}  {'L0 b/byte':>10}  "
          f"{'V2/L0':>7}  {'enc ms':>9}  {'dec ms':>9}  {'n_used':>7}  "
          f"{'cap hit':>8}  {'OK':>3}")

    for size in (4096, 8192, 16384):
        data = text(size)
        t0 = time.perf_counter()
        el, _ = l0_enc(data); assert l0_dec(el) == data
        l0_t = time.perf_counter() - t0
        l0_b = 8 * len(el) / size

        for cap in (128, 256, 512, 1024, 2048, 4096, 8192):
            try:
                t0 = time.perf_counter()
                enc, stats = v2_enc(data, max_opcodes=cap)
                enc_t = time.perf_counter() - t0
                t0 = time.perf_counter()
                dec = v2_dec(enc, max_opcodes=cap)
                dec_t = time.perf_counter() - t0
                ok = dec == data
                bpb = 8 * len(enc) / size
                ratio = bpb / l0_b if l0_b > 0 else 0.0
                cap_hit = stats["cap_frozen"]
                print(f"{size:>5} {cap:>5}  {bpb:>10.3f}  {l0_b:>10.3f}  "
                      f"{ratio:>7.3f}  {enc_t*1000:>7.1f}ms  {dec_t*1000:>7.1f}ms  "
                      f"{stats['n_final_opcodes']:>7}  "
                      f"{('YES' if cap_hit else 'no'):>8}  "
                      f"{'OK' if ok else 'FAIL':>3}")
            except Exception as e:
                print(f"{size:>5} {cap:>5}  ERROR: {type(e).__name__}: {e}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
