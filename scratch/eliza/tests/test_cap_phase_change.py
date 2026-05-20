"""tests/test_cap_phase_change.py — measure encode time vs VM steps to
reveal GPU-internal bottleneck phase changes across the cap sweep.

The cap-sweep showed a phase-change peak in encode time around the
cap that just-barely accommodates the natural n_used. Hypothesis:
* cap << natural: cap freezes early; fewer growths, fewer match
  recomputes, fewer steps.
* cap ≈ natural: every observed digram triggers growth + match
  recompute; maximum work per emission.
* cap >> natural: growth completes during input; subsequent emissions
  use stable match tensor; less work per emission.

This test measures per-(size, cap) the:
  * total encode time
  * VM steps (n_vm)
  * growth events (n_growth)
  * time per step
  * time per growth
  * "growth rate" (n_growth / n_vm)
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from eliza.gpu_codec_v2 import encode as v2_enc


def text(n: int) -> bytes:
    src = ROOT / "eliza" / "engine.py"
    with open(src, "rb") as f:
        d = f.read()
    while len(d) < n:
        d = d + d
    return d[:n]


def main() -> int:
    print("=== Cap phase-change analysis (V2 on text) ===\n")
    print(f"{'size':>5} {'cap':>5}  {'enc ms':>8}  {'n_vm':>5}  "
          f"{'n_grow':>7}  {'n_final':>8}  {'cap_hit':>8}  "
          f"{'us/step':>8}  {'us/grow':>8}  {'grow %':>7}")

    for size in (4096, 8192, 16384):
        data = text(size)
        for cap in (128, 256, 512, 1024, 2048, 4096, 8192):
            t0 = time.perf_counter()
            enc, stats = v2_enc(data, max_opcodes=cap)
            enc_t = time.perf_counter() - t0
            n_vm = stats["n_vm"]
            n_grow = stats["n_growth"]
            n_final = stats["n_final_opcodes"]
            cap_hit = stats["cap_frozen"]
            us_per_step = (enc_t * 1e6) / n_vm if n_vm > 0 else 0.0
            us_per_grow = (enc_t * 1e6) / n_grow if n_grow > 0 else 0.0
            grow_pct = 100.0 * n_grow / n_vm if n_vm > 0 else 0.0
            print(f"{size:>5} {cap:>5}  {enc_t*1000:>6.0f}ms  {n_vm:>5}  "
                  f"{n_grow:>7}  {n_final:>8}  "
                  f"{('YES' if cap_hit else 'no'):>8}  "
                  f"{us_per_step:>6.1f}µs  {us_per_grow:>6.1f}µs  "
                  f"{grow_pct:>6.1f}%")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
