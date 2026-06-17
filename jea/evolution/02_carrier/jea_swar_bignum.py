#!/usr/bin/env python3
"""jea_swar_bignum.py — the composition: N independent BIGNUM multiplies concurrently per register,
lane-isolated. Chains the SWAR lane-wise multiply into a per-lane schoolbook convolution + a
per-lane base-2^L carry. Same width ladder; at L=1 carryless it is N independent GF(2) clmuls.

Each lane runs its own bignum multiply: col[k] = sum_{i+j=k} a_lane[i]*b_lane[j] (lane-wise
bit-serial multiply-accumulate, plain add since the W=lane-width has room: W >= 2L+ceil(log2 K)),
then base-2^L carry-propagate per lane (carry stays in-lane: mask high part, shift down by L).
carryless: out[k] = col[k] mod 2^L (no propagate) = GF(2)[x] coefficient (L=1 -> mod 2 = clmul).
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp

FULL = np.uint64((1 << 64) - 1)

def _broadcast(bk, W):                       # fill each W-lane from its low bit (log W in-lane shift-ORs)
    f = bk; s = 1
    while s < W:
        f = (f | (f << np.uint64(s))) & FULL; s <<= 1
    return f

def swar_bignum_mul(A, B, L, K, N, W, carryless):
    """A,B: lists of K uint64 device arrays (limb p, N lanes packed in W-bit fields). Returns out
    limb words (each lane = that bignum's product limb)."""
    assert W & (W-1) == 0, f"W={W} must be a power of 2 (the doubling broadcast overshoots otherwise)"
    LANE_LO = np.uint64(sum(1 << (l*W) for l in range(N)))
    VAL = np.uint64(sum(((1 << L)-1) << (l*W) for l in range(N)))           # low L bits per lane
    HI  = np.uint64(sum((((1 << W)-1) ^ ((1 << L)-1)) << (l*W) for l in range(N)))  # bits >= L per lane
    Bsz = A[0].size; nout = 2*K - 1
    col = [cp.zeros(Bsz, cp.uint64) for _ in range(nout)]
    for i in range(K):
        for j in range(K):
            k = i + j
            for bit in range(L):              # lane-wise A[i]*B[j], bit-serial, into col[k]
                bk = (B[j] >> np.uint64(bit)) & LANE_LO
                addend = ((A[i] << np.uint64(bit)) & _broadcast(bk, W)) & FULL
                col[k] = (col[k] + addend) & FULL
    if carryless:
        return [(c & VAL) for c in col]
    out = []; carry = cp.zeros(Bsz, cp.uint64)
    for k in range(nout):
        c = (col[k] + carry) & FULL
        out.append(c & VAL)
        carry = ((c & HI) >> np.uint64(L)) & FULL     # per-lane carry (high part shifted down, in-lane)
    while int(carry.max()) > 0:                        # propagate the tail carry into further limbs
        out.append(carry & VAL)
        carry = ((carry & HI) >> np.uint64(L)) & FULL
    return out


def pack(vals, L, K, W):                     # vals: (B,N) python ints -> list of K uint64 words
    Bsz, N = len(vals), len(vals[0])
    A = []
    for p in range(K):
        word = np.zeros(Bsz, np.uint64)
        for b in range(Bsz):
            w = 0
            for l in range(N):
                w |= (((vals[b][l] >> (L*p)) & ((1 << L)-1)) << (l*W))
            word[b] = w
        A.append(cp.asarray(word))
    return A

def unpack(out, L, W, N):                     # out: list of limb words -> (B,N) ints
    Bsz = out[0].size; res = [[0]*N for _ in range(Bsz)]
    host = [o.get() for o in out]
    for b in range(Bsz):
        for l in range(N):
            v = 0
            for k in range(len(host)):
                v |= int((int(host[k][b]) >> (l*W)) & ((1 << L)-1)) << (L*k)
            res[b][l] = v
    return res

def clmul(a, b):
    r = 0; i = 0
    while b:
        if b & 1: r ^= a << i
        b >>= 1; i += 1
    return r


if __name__ == "__main__":
    rng = np.random.default_rng(0); Bsz = 256
    print("SWAR bignum multiply: N independent bignums multiplied concurrently per register\n")
    allok = True

    def cfg(L, K, W, N, carryless, name):
        global allok
        M = (1 << (L*K)) - 1
        vA = [[int(rng.integers(0, M+1)) for _ in range(N)] for _ in range(Bsz)]
        vB = [[int(rng.integers(0, M+1)) for _ in range(N)] for _ in range(Bsz)]
        A = pack(vA, L, K, W); B = pack(vB, L, K, W)
        out = swar_bignum_mul(A, B, L, K, N, W, carryless)
        got = unpack(out, L, W, N)
        if carryless:
            ref = [[clmul(vA[b][l], vB[b][l]) for l in range(N)] for b in range(Bsz)]
        else:
            ref = [[vA[b][l] * vB[b][l] for l in range(N)] for b in range(Bsz)]
        ok = (got == ref); allok &= ok
        print(f"  {name}: L={L} K={K} -> {N} bignums/register x {Bsz} words = {N*Bsz} bignum-muls, "
              f"lane-isolated == ref: {ok}")

    cfg(4, 4, 16, 4, False, "integer  ")          # W power-of-2 >= 2L+ceil(log2 K)
    cfg(8, 3, 32, 2, False, "integer  ")
    cfg(1, 8,  4, 16, True, "GF(2)clmul")    # 16 independent GF(2)[x] multiplies per register
    cfg(1, 12, 4, 16, True, "GF(2)clmul")

    print(f"\n  {'PASS' if allok else 'FAIL'} — multi-carrier bignum multiply: each lane runs its own")
    print(f"  schoolbook convolution + base-2^L carry, lane-isolated, exact. Carry mode = integer mul;")
    print(f"  carryless L=1 = N independent GF(2) clmuls per register. The carrier is now SWAR end-to-end")
    print(f"  (add + multiply), N carriers in flight, bottoming at GF(2) -- the substrate's home field.")
