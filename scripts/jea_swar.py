#!/usr/bin/env python3
"""jea_swar.py — SIMD-Within-A-Register for the carrier: process MULTIPLE independent bignums
(carriers) concurrently in one 32-bit register, lane-isolated. Walk the ladder TOP-DOWN
(annealing, one halving per rung, verify each): lane width L = 32 -> 16 -> 8 -> 4 -> 2 -> 1,
packing nlanes = 32/L carriers per word (1,2,4,8,16,32). The carry-isolation "pain" enters one
increment at a time; 1-bit (carryless XOR/AND = GF(2)) is earned LAST.

SWAR full-adder (parametric in lane width L), per lane, carry-in cin -> (sum, carry-out), with NO
carry crossing lane boundaries:
  notH = ~(top bit of each lane); low = (a&notH) + (b&notH) + cin    # low (L-1) bits + cin; can't
                                                                      #   cross (max 2^L-1 < 2^L)
  s    = low ^ (a&H) ^ (b&H)                                          # add top bits mod 2 -> (a+b+cin) mod 2^L
  cfl  = ((low&H) >> (L-1)) & LANE_LO ; at,bt = a,b top bits at lane-low
  cout = (at&bt) | (cfl & (at^bt))                                    # carry-out per lane, at lane-low
At L=1: notH=0 -> s = cin^a^b (XOR full-adder), cout=(a&b)|(cin&(a^b)) (AND/maj) = GF(2). One formula,
the whole ladder; the GF(2) carryless reading at L=1 just keeps s and drops cout.
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp

U32 = (1 << 32) - 1

def masks(L):
    nl = 32 // L
    lane_lo = sum(1 << (l*L) for l in range(nl))            # bit 0 of each lane
    H = sum(1 << (l*L + L - 1) for l in range(nl))          # top bit of each lane
    return nl, np.uint32(lane_lo), np.uint32(H), np.uint32((~H) & U32)

def swar_add(a, b, cin, L, lane_lo, H, notH):
    """a,b,cin: uint32 device arrays (cin = carry bits at lane-low). Returns (s, cout) per lane."""
    low = (a & notH) + (b & notH) + cin                      # uint32; per-lane, no cross (<2^L)
    s = (low ^ (a & H) ^ (b & H)).astype(cp.uint32)
    cfl = ((low & H) >> np.uint32(L-1)) & lane_lo
    at = ((a & H) >> np.uint32(L-1)) & lane_lo
    bt = ((b & H) >> np.uint32(L-1)) & lane_lo
    cout = ((at & bt) | (cfl & (at ^ bt))).astype(cp.uint32)
    return s, cout

# ---- pack/unpack nlanes independent bignums (each K limbs of L bits) into K packed u32 words ----
def pack(vals, L, K):
    nl = 32 // L; B = 1 << L
    words = np.zeros(K, np.uint32)
    for p in range(K):
        w = 0
        for l in range(nl):
            w |= ((vals[l] >> (L*p)) & (B-1)) << (l*L)
        words[p] = w
    return cp.asarray(words, cp.uint32)

def unpack(words, L, nl):
    B = 1 << L; w = words.get()
    out = [0]*nl
    for p in range(len(w)):
        for l in range(nl):
            out[l] |= int((int(w[p]) >> (l*L)) & (B-1)) << (L*p)
    return out

def bignum_swar_add(A, B, L, K):
    nl, lane_lo, H, notH = masks(L)
    cin = cp.zeros(1, cp.uint32)
    out = []
    for p in range(K):
        s, cout = swar_add(A[p:p+1], B[p:p+1], cin, L, lane_lo, H, notH)
        out.append(s); cin = cout
    out.append(cin)                                          # final carry word
    return cp.concatenate(out)


if __name__ == "__main__":
    print("SWAR carrier: N independent bignums added concurrently per 32-bit register, lane-isolated.")
    print("Walking the ladder TOP-DOWN (verify each rung before the next):\n")
    rng = np.random.default_rng(0)
    K = 6                                                     # limbs per bignum (per lane)
    allok = True
    for L in (32, 16, 8, 4, 2, 1):
        nl = 32 // L; B = 1 << L
        def randbig():                                        # K random L-bit limbs -> one bignum
            return sum(int(rng.integers(0, B)) << (L*p) for p in range(K))
        vA = [randbig() for _ in range(nl)]                   # nl independent bignums
        vB = [randbig() for _ in range(nl)]
        A = pack(vA, L, K); Bw = pack(vB, L, K)
        outw = bignum_swar_add(A, Bw, L, K)
        got = unpack(outw, L, nl)
        ref = [vA[l] + vB[l] for l in range(nl)]
        ok = (got == ref); allok &= ok
        note = "  (1 lane: baseline, no cross-lane carry)" if L == 32 else \
               ("  <- L=1: XOR/AND full-adder = GF(2) (carryless = keep sum, drop carry)" if L == 1 else "")
        print(f"  L={L:2d}: {nl:2d} carriers/register, lane-isolated add of {nl} bignums == per-lane ref: {ok}{note}")

    print(f"\n  {'PASS' if allok else 'FAIL'} — ONE parametric SWAR full-adder, the whole ladder 32->16->8->4->2->1.")
    print(f"  Carry stays inside each lane (verified at every width); packing density 1->2->4->8->16->32")
    print(f"  carriers per register. At L=1 the adder IS GF(2) (XOR sum / AND carry) -- the descent's floor,")
    print(f"  reached only after walking all the carry-isolation pain above it.")
