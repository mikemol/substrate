#!/usr/bin/env python3
"""jea_swar_mul.py — SWAR MULTIPLY down the same ladder: N independent products a_l*b_l computed
concurrently per register, lane-isolated. Walk TOP-DOWN (anneal, verify each rung): lane value
width L = 32->16->8->4->2->1, packing nlanes = 32/L = 1,2,4,8,16,32 carriers (in a 64-bit container).

The pain is NOT add's carry-isolation -- it's that L-bit x L-bit = 2L-bit products SPILL into the
next lane. Fix: SPACE each lane to W = 2L bits (value in the low L). Then every partial product
stays inside its lane (a_l*b_l < 2^W, and the running sum is monotone <= a_l*b_l), so the
accumulation is a PLAIN add -- no cross-lane carry. The remaining trick is the per-lane BROADCAST
of "bit k of b" to a full-lane mask (log(W) in-lane shift-ORs). Bit-serial: for k in 0..L-1, add
(a << k) wherever b's bit k is set, lane-isolated.

At L=1: W=2, one step (k=0), broadcast bit0 of b, addend = a & (b filled) => R = a AND b = GF(2)
scalar multiply (1-bit x 1-bit = AND). 32 GF(2) products per register, carryless, no spill -- the
floor, reached after the spacing/broadcast pain of the wider rungs.
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp

FULL = np.uint64((1 << 64) - 1)

def swar_mul(a, b, L):
    """a,b: uint64 device arrays, each word packs nlanes=32/L values in W=2L-bit lanes (value in
    low L bits). Returns R with R's W-lane l = a_l * b_l (2L-bit product)."""
    W = 2*L; nl = 64 // W
    LANE_LO = np.uint64(sum(1 << (l*W) for l in range(nl)))
    R = cp.zeros_like(a)
    for k in range(L):
        bitk = (b >> np.uint64(k)) & LANE_LO          # bit k of each lane's b-value, at lane-low
        filled = bitk; s = 1                          # broadcast it to a full W-lane mask (in-lane)
        while s < W:
            filled = (filled | (filled << np.uint64(s))) & FULL
            s <<= 1
        addend = ((a << np.uint64(k)) & filled) & FULL # a<<k where b bit k set; stays in-lane
        R = (R + addend) & FULL                        # plain add: partial product < 2^W, no spill
    return R

def pack(words_vals, L):
    """words_vals: (B, nlanes) array of L-bit values -> (B,) uint64, value l in low L of W-lane l."""
    W = 2*L; nl = words_vals.shape[1]; B = words_vals.shape[0]
    out = np.zeros(B, np.uint64)
    for l in range(nl):
        out |= (words_vals[:, l].astype(np.uint64) & np.uint64((1 << L)-1)) << np.uint64(l*W)
    return cp.asarray(out)

def unpack(words, L, nl):
    W = 2*L; w = words.get(); M = (1 << W) - 1
    return np.stack([((w >> (l*W)) & M) for l in range(nl)], axis=1)


if __name__ == "__main__":
    print("SWAR multiply: N independent products per 64-bit register, lane-isolated.")
    print("Walking the ladder TOP-DOWN (verify each rung):\n")
    rng = np.random.default_rng(0); B = 4096
    allok = True
    for L in (32, 16, 8, 4, 2, 1):
        W = 2*L; nl = 64 // W; M = (1 << L) - 1
        a = rng.integers(0, 1 << L, size=(B, nl), dtype=np.uint64) if L < 64 else None
        a = rng.integers(0, M+1, size=(B, nl)).astype(np.uint64)
        b = rng.integers(0, M+1, size=(B, nl)).astype(np.uint64)
        R = swar_mul(pack(a, L), pack(b, L), L)
        got = unpack(R, L, nl)
        ref = (a.astype(object) * b.astype(object))    # exact (Python ints) per lane
        ok = bool((got.astype(object) == ref).all()); allok &= ok
        note = "  (1 lane: baseline)" if L == 32 else \
               ("  <- L=1: a AND b = GF(2) scalar multiply (carryless, no spill)" if L == 1 else "")
        print(f"  L={L:2d}: {nl:2d} carriers/register x {B} words = {nl*B:>6} products, lane-isolated == ref: {ok}{note}")

    print(f"\n  {'PASS' if allok else 'FAIL'} — SWAR multiply, ladder 32->16->8->4->2->1. The spill pain is")
    print(f"  handled by SPACING (W=2L lanes => plain-add accumulation) + per-lane broadcast; packing")
    print(f"  1->2->4->8->16->32 carriers/register. At L=1 it IS GF(2) scalar multiply (AND). Both the add")
    print(f"  and multiply ladders bottom out at GF(2) -- the substrate's home field, max packing, carry-free.")
