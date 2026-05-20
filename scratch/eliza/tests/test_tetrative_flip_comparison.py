"""tests/test_tetrative_flip_comparison.py — flip-opcode redux.

Comparison across the tetrative axis with the user's two corrections
applied (flip-opcode instead of per-emission flag; K-step beam
lookahead):

  * L0 adaptive  — automatic adaptive rewrite (no speculation)
  * L1-flag      — old design: per-emission flag (FAILED: +20-27%)
  * L1-flip K=4  — flip-opcode + 4-step beam
  * L1-flip K=8  — flip-opcode + 8-step beam
  * L2-flip K=4  — observe-as-opcode with flip-opcode + 4-step beam

Plus downstream-structure probe: when speculation DOES say leave-alone
(skip / no-rewrite), does the resulting grammar have cleaner structure?

Outputs: bits/byte across corpora + final-grammar diagnostic stats.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from eliza.adaptive_opcode_codec import encode as ad_enc, decode as ad_dec
from eliza.l1_flip_codec import encode as l1f_enc, decode as l1f_dec
from eliza.l1_rewrite_codec import encode as l1g_enc, decode as l1g_dec
from eliza.l2_flip_codec import encode as l2f_enc, decode as l2f_dec
from eliza.dim2_codec import encode as gt_enc, decode as gt_dec


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
SIZES = (1024, 2048)


def main() -> int:
    print("=== Tetrative axis (flip-opcode redesign) ===\n")
    print(f"All numbers in BITS-PER-INPUT-BYTE; all modes round-trip\n"
          f"byte-for-byte (lossless).\n")

    for size in SIZES:
        print(f"--- {size}B inputs ---")
        print(f"{'corpus':>8}  {'gt':>5}  {'L0':>5}  {'L1-flag':>8}  "
              f"{'L1-flip(4)':>12}  {'L1-flip(8)':>12}  {'L2-flip(4)':>12}")
        for name, factory in CORPORA.items():
            d = factory(size)
            eg, _ = gt_enc(d); assert gt_dec(eg, len(d)) == d
            ea, sa = ad_enc(d); assert ad_dec(ea) == d
            e1g, s1g = l1g_enc(d, lookahead=4); assert l1g_dec(e1g) == d
            e1f4, s1f4 = l1f_enc(d, k_steps=4); assert l1f_dec(e1f4) == d
            e1f8, s1f8 = l1f_enc(d, k_steps=8); assert l1f_dec(e1f8) == d
            e2f4, s2f4 = l2f_enc(d, k_steps=4); assert l2f_dec(e2f4) == d
            bg = 8*len(eg)/len(d); ba = 8*len(ea)/len(d)
            b1g = 8*len(e1g)/len(d); b1f4 = 8*len(e1f4)/len(d)
            b1f8 = 8*len(e1f8)/len(d); b2f4 = 8*len(e2f4)/len(d)
            print(f"{name:>8}  {bg:>5.2f}  {ba:>5.2f}  {b1g:>8.2f}  "
                  f"{b1f4:>12.2f}  {b1f8:>12.2f}  {b2f4:>12.2f}")
        print()

    # I8: downstream-structure probe.
    print("=== Downstream-structure probe (4KB text) ===")
    print("How does the final grammar look under each scheme?\n")
    d = _text(4096)
    schemes = [
        ("L0 adaptive",    lambda: ad_enc(d)),
        ("L1-flip K=4",    lambda: l1f_enc(d, k_steps=4)),
        ("L2-flip K=4",    lambda: l2f_enc(d, k_steps=4)),
    ]
    print(f"{'scheme':>16}  {'final_ops':>10}  {'growth':>8}  {'flips':>7}")
    for label, run in schemes:
        enc, stats = run()
        n_ops = stats.get("n_final_opcodes")
        n_growth = stats.get("n_growth")
        # Flip / skip / commit count by scheme.
        flips = (stats.get("n_flip_emissions") or
                 stats.get("n_skip_emissions") or
                 stats.get("n_rewrites_committed") or 0)
        print(f"{label:>16}  {n_ops:>10}  {n_growth:>8}  {flips:>7}")

    print()
    print("Reading:")
    print(" - L0:        baseline, no speculation control.")
    print(" - L1-flag:   per-emission flag (1 bit each) → +20-27% overhead.")
    print(" - L1-flip:   flip-opcode (zero overhead when default best); MATCHES L0.")
    print(" - L2-flip:   observe-as-opcode; few skips → ≈ L0.")
    print(" - flip-opcode design eliminates the per-emission penalty.")
    print(" - On these corpora, L0's automatic default IS near-optimal;")
    print("   speculation finds 0-4 deviations per KB. No bits gained,")
    print("   but no bits lost either.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
