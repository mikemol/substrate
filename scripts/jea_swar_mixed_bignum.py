#!/usr/bin/env python3
"""jea_swar_mixed_bignum.py — MIXED-width bignum multiply: carriers of DIFFERENT precision, each a
multi-limb bignum, multiplied concurrently in one register, with PER-LANE carry-chaining.

This is the composition of the two prior mixed pieces:
  - mixed multiply (jea_swar_mixed_mul): per-distinct-width passes for the lane-wise products, because
    the global shifts overshoot a narrow lane into a wider neighbor.
  - bignum carry (jea_swar_bignum): per-lane base-2^L carry-propagate down the convolution columns.

The NEW pain is exactly the carry SHIFT. Uniform bignum carries with one global `>> L` (every lane
shares L). Across MIXED lanes each lane must shift its high part down by ITS OWN L -- a single global
shift over/under-shifts the wrong-width lanes. Fix (same move as the mixed multiply): group lanes by
(L,W), do the uniform carry shift per group, OR the disjoint results.

  carry = OR_g ((c & GRP_HI_g) >> L_g)

Why it stays in-lane: `c & GRP_HI_g` zeroes every non-group-g bit; `>> L_g` then moves group g's high
bits [off+L, off+W) down to [off, off+W-L) -- still inside each lane (lowest lands at off), and it
cannot reach another group because those bits were already zeroed. Groups occupy disjoint bit ranges,
so the OR is clean. The single `col[k] + carry` add is lane-safe iff each room obeys
W >= 2L + 1 + ceil(log2 K) (col[k] + carry < 2^W) -- asserted, not assumed (the overshoot lesson).

So BOTH the multiply convolution and the carry-propagate cost #distinct-widths "divergent" passes --
the same warp-divergence-as-Pareto-knob as the single-limb mixed multiply.
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from collections import defaultdict
from math import ceil, log2

FULL = np.uint64((1 << 64) - 1)


def min_room(L, K):
    need = 2 * L + 1 + (ceil(log2(K)) if K > 1 else 0)   # W s.t. col[k]+carry < 2^W (no bleed)
    W = 1
    while W < need:
        W <<= 1
    return W


def build_masks(layout):
    """layout: [(off, L, W)] tiling 64. Returns (VAL, grp) where VAL = union of low-L limb fields and
    grp = per-distinct-(L,W) [(L, W, GRPVAL, GRP_LO, GRP_HI)]."""
    VAL = 0
    for off, L, W in layout:
        VAL |= ((1 << L) - 1) << off
        assert W & (W - 1) == 0, f"room W={W} must be a power of 2 (broadcast overshoots otherwise)"
    groups = defaultdict(list)
    for off, L, W in layout:
        groups[(L, W)].append(off)
    grp = []
    for (L, W), offs in groups.items():
        GRPVAL = sum(((1 << W) - 1) << o for o in offs)                 # full rooms of this group
        GRP_LO = sum(1 << o for o in offs)                             # low bit of each group lane
        GRP_HI = sum((((1 << W) - 1) ^ ((1 << L) - 1)) << o for o in offs)  # bits [L,W) per group lane
        grp.append((L, W, np.uint64(GRPVAL), np.uint64(GRP_LO), np.uint64(GRP_HI)))
    return np.uint64(VAL), grp


def _broadcast(bk, W):                                  # fill each W-window from its low bit (W pow2)
    f = bk; s = 1
    while s < W:
        f = (f | (f << np.uint64(s))) & FULL; s <<= 1
    return f


def mul_accum(col, Ai, Bj, grp):
    """col += Ai * Bj, lane-wise, per width-group (the mixed single-limb multiply). Plain add: each
    product < 2^W, columns accumulate within the room."""
    for (L, W, GRPVAL, GRP_LO, GRP_HI) in grp:
        ag = Ai & GRPVAL; bg = Bj & GRPVAL                              # isolate this group
        for k in range(L):
            bk = (bg >> np.uint64(k)) & GRP_LO                          # bit k of each lane's b
            f = _broadcast(bk, W)                                       # broadcast to full W-window
            addend = ((ag << np.uint64(k)) & f) & FULL                  # a<<k where b bit k set, in-lane
            col = (col + addend) & FULL
    return col


def carry_propagate(cols, VAL, grp):
    """Down the convolution columns: c = col[k] + carry; emit low-L limb (c & VAL); carry = high part
    shifted down by L PER GROUP, OR'd. Tail loop flushes the final carry into further limbs."""
    out = []; carry = cp.zeros_like(cols[0])
    for k in range(len(cols)):
        c = (cols[k] + carry) & FULL
        out.append(c & VAL)
        carry = cp.zeros_like(c)
        for (L, W, GRPVAL, GRP_LO, GRP_HI) in grp:
            carry = (carry | ((c & GRP_HI) >> np.uint64(L))) & FULL     # per-group shift, OR disjoint
    while int(carry.max()) > 0:                                         # flush tail carry
        out.append(carry & VAL)
        nxt = cp.zeros_like(carry)
        for (L, W, GRPVAL, GRP_LO, GRP_HI) in grp:
            nxt = (nxt | ((carry & GRP_HI) >> np.uint64(L))) & FULL
        carry = nxt
    return out


def swar_mixed_bignum_mul(A, B, layout, K):
    """A,B: K register words (word p = limb p, base 2^L per lane). Returns product limb words."""
    VAL, grp = build_masks(layout)
    for off, L, W in layout:                                           # the no-bleed constraint
        assert W >= 2 * L + 1 + (ceil(log2(K)) if K > 1 else 0), \
            f"lane @{off}: room W={W} < 2L+1+ceil(log2 K) for L={L},K={K} -> carry would bleed"
    nout = 2 * K - 1
    cols = [cp.zeros_like(A[0]) for _ in range(nout)]
    for i in range(K):
        for j in range(K):
            cols[i + j] = mul_accum(cols[i + j], A[i], B[j], grp)
    return carry_propagate(cols, VAL, grp)


def pack(vals, layout, K):
    """vals: list (batch) of {off: int lane-bignum value}. Returns K register words."""
    B = len(vals); words = []
    for p in range(K):
        word = np.zeros(B, np.uint64)
        for b in range(B):
            w = 0
            for off, L, W in layout:
                w |= ((vals[b][off] >> (L * p)) & ((1 << L) - 1)) << off
            word[b] = w
        words.append(cp.asarray(word))
    return words


def unpack(out, layout):
    """out: product limb words. Returns list (batch) of {off: int product value}."""
    host = [o.get() for o in out]; B = out[0].size
    res = [dict() for _ in range(B)]
    for b in range(B):
        for off, L, W in layout:
            v = 0
            for k in range(len(host)):
                v |= int((int(host[k][b]) >> off) & ((1 << L) - 1)) << (L * k)
            res[b][off] = v
    return res


if __name__ == "__main__":
    # three distinct widths -> 3 divergent passes for BOTH multiply and carry. Rooms obey
    # W >= 2L+1+ceil(log2 K); L in {4,2,1} each carry-chained (L=1 here is binary integer, not GF(2)).
    K = 3
    layout = [(0, 4, 16), (16, 2, 8), (24, 2, 8), (32, 1, 8),
              (40, 1, 8), (48, 1, 8), (56, 2, 8)]              # 16+8+8+8+8+8+8 = 64
    assert sum(W for _, _, W in layout) == 64
    print("mixed-width SWAR bignum multiply: lanes of different precision, each a K-limb bignum,")
    print(f"  carry-chained PER LANE (per-distinct-width carry shift). K={K} limbs, layout {layout}\n")

    rng = np.random.default_rng(0); B = 20000
    vA = [{} for _ in range(B)]; vB = [{} for _ in range(B)]
    for off, L, W in layout:
        hi = 1 << (L * K)                                      # lane bignum value < 2^(L*K)
        for b in range(B):
            vA[b][off] = int(rng.integers(0, hi)); vB[b][off] = int(rng.integers(0, hi))
    A = pack(vA, layout, K); B_ = pack(vB, layout, K)
    out = swar_mixed_bignum_mul(A, B_, layout, K)
    got = unpack(out, layout)

    allok = True
    seen = set()
    for off, L, W in layout:
        ok = all(got[b][off] == vA[b][off] * vB[b][off] for b in range(B))
        allok &= ok
        tag = "" if (L, W) in seen else f"  (group L={L}/W={W}: a distinct carry-shift pass)"
        seen.add((L, W))
        print(f"  lane @{off:<2} L={L} room {W:>2}: bignum product == a*b across {B} words : {ok}{tag}")

    print(f"\n  {'PASS' if allok else 'FAIL'} — mixed-width bignum multiply with per-lane carry-chaining.")
    print(f"  Each lane runs its own K-limb schoolbook convolution + base-2^L carry; the carry SHIFT is")
    print(f"  per-distinct-width (group by (L,W), shift down by that L, OR disjoint). {len(set((L,W) for _,L,W in layout))} distinct widths")
    print(f"  => {len(set((L,W) for _,L,W in layout))} divergent passes for BOTH the convolution and the carry -- the same #distinct-widths")
    print(f"  Pareto knob as the single-limb mixed multiply. Carrier is now SWAR end-to-end at mixed precision.")
