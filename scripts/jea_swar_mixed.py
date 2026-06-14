#!/usr/bin/env python3
"""jea_swar_mixed.py — MIXED-width SWAR: carriers of DIFFERENT precisions packed in one register,
processed concurrently, lane-isolated at the heterogeneous boundaries. Start: a 32-bit lane + a
16-bit lane + two 8-bit lanes sharing a 64-bit register (32+16+8+8 = 64).

The SWAR full-adder is MASK-DRIVEN, so it is layout-agnostic: with H = top bit of EACH lane and
notH = ~H, the carry still can't cross a boundary (each lane's low-(w-1)-bit sum < 2^w stays inside
its own bit range, the carry landing in that lane's cleared top bit, never the next lane's low
bit). So mixed widths need only a per-lane mask set -- the same formula:
  low = (a&notH)+(b&notH);  s = low ^ (a&H) ^ (b&H)  (= per-lane (a+b) mod 2^w, no bleed)
  cout = (a&H & b&H) | ((low&H) & ((a&H)^(b&H)))      (= carry-out, at each lane's top-bit position)
This is pay-for-what-you-use at the LANE level: each carrier sits at exactly the width it needs.
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp

FULL = np.uint64((1 << 64) - 1)

def masks(layout):
    """layout: [(offset, width), ...] tiling 64 bits. Returns (H, notH, LANE_LO, VAL) as uint64."""
    H = LANE_LO = VAL = 0
    for off, wid in layout:
        H |= 1 << (off + wid - 1)               # top bit of this lane
        LANE_LO |= 1 << off                      # low bit of this lane
        VAL |= ((1 << wid) - 1) << off           # all bits of this lane
    return np.uint64(H), np.uint64((~H) & int(FULL)), np.uint64(LANE_LO), np.uint64(VAL)

def swar_add_mixed(a, b, H, notH):
    low = (a & notH) + (b & notH)                # per-lane low sum; no cross-lane carry
    s = (low ^ (a & H) ^ (b & H)) & FULL         # per-lane (a+b) mod 2^w
    aH, bH, cfl = (a & H), (b & H), (low & H)
    cout = ((aH & bH) | (cfl & (aH ^ bH))) & FULL  # carry-out, bit at each lane's top position
    return s, cout


if __name__ == "__main__":
    layout = [(0, 32), (32, 16), (48, 8), (56, 8)]    # 32 + 16 + 8 + 8 = 64
    H, notH, LANE_LO, VAL = masks(layout)
    rng = np.random.default_rng(0); B = 100000
    print("mixed-width SWAR: lanes of 32 / 16 / 8 / 8 bits sharing one 64-bit register\n")
    print(f"  layout {layout}   (H={hex(int(H))})\n")

    # random per-lane values, packed into one 64-bit word each
    vals_a = {off: rng.integers(0, 1 << wid, size=B, dtype=np.uint64) for off, wid in layout}
    vals_b = {off: rng.integers(0, 1 << wid, size=B, dtype=np.uint64) for off, wid in layout}
    a = cp.zeros(B, cp.uint64); b = cp.zeros(B, cp.uint64)
    for off, wid in layout:
        a |= cp.asarray(vals_a[off].astype(np.uint64)) << np.uint64(off)
        b |= cp.asarray(vals_b[off].astype(np.uint64)) << np.uint64(off)

    s, cout = swar_add_mixed(a, b, H, notH)
    sh, ch = s.get(), cout.get()
    allok = True
    print(f"  {'lane':>10} {'sum mod 2^w':>14} {'carry-out':>12}")
    for off, wid in layout:
        got_sum = (sh >> off) & ((1 << wid) - 1)
        got_cout = (ch >> (off + wid - 1)) & 1
        full = vals_a[off].astype(object) + vals_b[off].astype(object)
        ref_sum = full & ((1 << wid) - 1)
        ref_cout = full >> wid
        ok = bool((got_sum == ref_sum).all() and (got_cout == ref_cout).all()); allok &= ok
        print(f"  {wid:>3}-bit @{off:<2}  {'exact' if (got_sum==ref_sum).all() else 'WRONG':>14} "
              f"{'exact' if (got_cout==ref_cout).all() else 'WRONG':>12}   ({'OK' if ok else 'FAIL'})")

    print(f"\n  {'PASS' if allok else 'FAIL'} — heterogeneous lanes (32/16/8/8) add concurrently in one")
    print(f"  register, each lane's sum mod 2^w AND carry-out exact, NO bleed across uneven boundaries.")
    print(f"  Same mask-driven full-adder as uniform SWAR; the layout is just a per-lane mask set.")
    print(f"  => carriers can be packed at MIXED precisions (pay-for-what-you-use per lane).")
