#!/usr/bin/env python3
"""jea_swar_mixed_mul.py — MIXED-width SWAR multiply: carriers of different precisions multiplied
concurrently in one register, lane-isolated.

Two facts worked out (not assumed):
  1. TILING: products double, so the PRODUCT ROOMS (2L bits each) must tile the register, not the
     operand widths. In a 64-bit register the geometric fit is operand widths 16/8/4/2/1/1 -> rooms
     32/16/8/4/2/2 = 64. (Same operand ladder as the add-conclusion, but the top is 16 not 32
     because each product room is 2L -- product-doubling halves what the top lane can be.)
  2. NOT as simple as mixed ADD: add is mask-driven and single-pass because its carry stays in-lane.
     MULTIPLY uses global shifts (a<<k and the bit-broadcast), which OVERSHOOT narrow lanes into wide
     ones when widths differ. So a single pass is NOT lane-safe. Clean fix: one SWAR pass per DISTINCT
     width (uniform within each, masked to that width's lanes) -- a small constant number of passes.

Within a width-group everything is uniform (the proven uniform SWAR multiply); masking to the group
zeroes other groups so the global shift can't reach them. Products of disjoint lanes are combined by
plain add. At width 1 the lane multiply is AND = GF(2).
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from collections import defaultdict

M64 = np.uint64((1 << 64) - 1)

def mixed_swar_mul(a, b, layout):
    """layout: [(off, L, W)] with W a power of 2, W>=2L (W>=1 for L=1), sum(W)=64. Each lane: L-bit
    operand in low L bits of a W-bit product room at `off`. Returns R with each lane's a_l*b_l."""
    R = cp.zeros_like(a)
    groups = defaultdict(list)
    for off, L, W in layout:
        groups[(L, W)].append(off)
    for (L, W), offs in groups.items():                 # one SWAR pass per distinct width
        GRPVAL = np.uint64(sum(((1 << W)-1) << o for o in offs))   # room masks for this group
        GRP_LO = np.uint64(sum(1 << o for o in offs))              # low bit of each group lane
        ag = a & GRPVAL; bg = b & GRPVAL                           # isolate the group (zero others)
        for k in range(L):
            bk = (bg >> np.uint64(k)) & GRP_LO          # bit k of each group lane's operand, at lane-low
            f = bk; s = 1                                # broadcast to full W-lane (uniform W, power of 2)
            while s < W:
                f = (f | (f << np.uint64(s))) & M64; s <<= 1
            addend = ((ag << np.uint64(k)) & f) & M64
            R = (R + addend) & M64                       # in-lane accumulate; groups disjoint
    return R


if __name__ == "__main__":
    layout = [(0, 16, 32), (32, 8, 16), (48, 4, 8), (56, 2, 4), (60, 1, 2), (62, 1, 2)]  # rooms = 64
    rng = np.random.default_rng(0); B = 100000
    print("mixed-width SWAR multiply in a 64-bit register: operand widths 16/8/4/2/1/1")
    print(f"  layout (off,L,room): {layout}   (sum rooms = {sum(W for _,_,W in layout)})\n")
    va = {off: rng.integers(0, 1 << L, size=B, dtype=np.uint64) for off, L, W in layout}
    vb = {off: rng.integers(0, 1 << L, size=B, dtype=np.uint64) for off, L, W in layout}
    a = cp.zeros(B, cp.uint64); b = cp.zeros(B, cp.uint64)
    for off, L, W in layout:
        a |= cp.asarray(va[off]) << np.uint64(off); b |= cp.asarray(vb[off]) << np.uint64(off)
    R = mixed_swar_mul(a, b, layout); rh = R.get()
    allok = True
    for off, L, W in layout:
        got = (rh >> off) & ((1 << W) - 1)
        ref = va[off].astype(object) * vb[off].astype(object)
        ok = bool((got == ref).all()); allok &= ok
        tag = "  (GF(2): a AND b)" if L == 1 else ""
        print(f"  {L}-bit operand @{off:<2} room {W:>2}: product lane-isolated == a*b : {ok}{tag}")
    print(f"\n  {'PASS' if allok else 'FAIL'} — mixed-width multiply: 16/8/4/2/1/1 carriers multiplied")
    print(f"  concurrently in one 64-bit register, each product lane-isolated and exact (1-bit = AND/GF2).")
    print(f"  HONEST: unlike mixed ADD (single mask-driven pass), mixed MUL needs one pass per distinct")
    print(f"  width (global shifts overshoot narrow->wide); product-doubling caps the top operand at 16 (vs add's 32).")
