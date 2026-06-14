#!/usr/bin/env python3
"""jea_carrier_base.py — the limb carrier parametric in base B = 2^w. The least-cost descent
8->4->2->1: the dp4a CONVOLUTION KERNEL IS UNCHANGED (it multiplies byte-valued limbs, base-
agnostic); only the host-side carry takes (w) and a carry/carryless mode. Descending the width
ladder is changing one parameter.

  * carry mode, base B: integer multiply -- the SAME value a*b at every w (only the limb stream
    differs). w in {8,4,2,1} all reconstruct to a*b.
  * carryless mode, w=1: GF(2) polynomial multiply (out[k] = col[k] mod 2, no propagation) -- the
    substrate's home field. The big-value carrier and the F2 substrate UNIFY at w=1.

Width w (base B) and the carry/carryless mode are controller GAUGES; one parametric carrier, never
per-width forks.
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
import jea_core

# UNCHANGED from the 8-bit carrier: dp4a convolution over byte-valued limbs (any base B<=256).
_SRC = r'''
extern "C" __global__
void bmul_dp4a(const unsigned char* a, int La, const unsigned char* b, int Lb,
               unsigned int* col, int Lc)
{
    int k = blockIdx.x*blockDim.x + threadIdx.x; if (k >= Lc) return;
    int i_lo = max(0, k-(Lb-1)), i_hi = min(k, La-1);
    unsigned int acc = 0;
    for (int i = i_lo; i <= i_hi; i += 4) {
        unsigned int pa = 0, pb = 0;
        #pragma unroll
        for (int l = 0; l < 4; l++) {
            int ia = i+l, ib = k-(i+l);
            unsigned int av = (ia <= i_hi && ia < La) ? a[ia] : 0;
            unsigned int bv = (ib >= 0 && ib < Lb)    ? b[ib] : 0;
            pa |= av << (8*l); pb |= bv << (8*l);
        }
        acc = __dp4a(pa, pb, acc);
    }
    col[k] = acc;
}
'''
_mul = jea_core.build_kernel(_SRC, "bmul_dp4a")


def to_limbs(v, w):
    """base-B=2^w little-endian limbs, each in [0,B) stored as uint8 (B<=256)."""
    B = 1 << w
    if v == 0: return cp.zeros(1, cp.uint8)
    out = []
    while v: out.append(v & (B-1)); v >>= w
    return cp.asarray(out, cp.uint8)

def from_limbs(arr, w):
    v = 0
    for d in reversed(arr.get().tolist()): v = (v << w) | d    # Horner
    return v

def _trim(u8):
    nz = cp.nonzero(u8)[0]
    return u8[:int(nz[-1])+1] if nz.size else u8[:1]


def resolve(col, w, carryless):
    """base-B carry (or carryless mod-B). Parallel scatter+ripple; one parameter w."""
    B = 1 << w
    if carryless:                                 # GF(2)[x] at w=1: coefficient mod B, no propagate
        return _trim((col % B).astype(cp.uint8))
    colmax = int(col.max()) if col.size else 0
    me = 1
    while B**me <= colmax: me += 1                 # base-B digits of the largest column
    Lc = int(col.size); acc = cp.zeros(Lc + me, cp.uint64); Bc = col.astype(cp.uint64)
    for e in range(me):                            # scatter digit e of col[k] to position k+e
        acc[e:e+Lc] += (Bc // (B**e)) % B
    while int(acc.max()) >= B:                      # parallel ripple, base B
        carry = acc // B; acc = acc % B; acc[1:] += carry[:-1]
    return _trim(acc.astype(cp.uint8))


def gpu_mul(a_limbs, b_limbs, w, carryless=False):
    La, Lb = int(a_limbs.size), int(b_limbs.size); Lc = La+Lb-1
    col = cp.zeros(Lc, cp.uint32)
    _mul(((Lc+255)//256,), (256,), (a_limbs, np.int32(La), b_limbs, np.int32(Lb), col, np.int32(Lc)))
    cp.cuda.Stream.null.synchronize()
    return resolve(col, w, carryless)


def clmul(a, b):                                   # GF(2) carryless reference
    r = 0; i = 0
    while b:
        if b & 1: r ^= a << i
        b >>= 1; i += 1
    return r


if __name__ == "__main__":
    a = 7**500; b = 11**500
    print("base-parametric limb carrier (B=2^w): one kernel, descend the ladder by changing w\n")
    print("  INTEGER multiply -- same value a*b at every width (only the limb stream differs):")
    allok = True
    for w in (8, 4, 2, 1):
        al, bl = to_limbs(a, w), to_limbs(b, w)
        prod = gpu_mul(al, bl, w, carryless=False)
        ok = (from_limbs(prod, w) == a*b); allok &= ok
        print(f"     w={w} (B={1<<w:>3}): a={al.size:>5} limbs, b={bl.size:>5} -> {prod.size:>5} limbs   == a*b: {ok}")

    print("\n  CARRYLESS w=1 -- GF(2)[x] polynomial multiply (the substrate's F2 home field):")
    al, bl = to_limbs(a, 1), to_limbs(b, 1)
    poly = gpu_mul(al, bl, 1, carryless=True)
    gfok = (from_limbs(poly, 1) == clmul(a, b)); allok &= gfok
    print(f"     w=1 carryless: {poly.size} bit-limbs == clmul(a,b) (GF(2) reference): {gfok}")
    print(f"     (multiply=AND, add=XOR, no carry -- this is the int1 XOR-popcount / binary-tensor path)")

    print(f"\n  {'PASS' if allok else 'FAIL'} — ONE carrier, ONE unchanged dp4a kernel; 8->4->2->1 is the base")
    print(f"  parameter w; carry mode = exact integer at every width, carryless w=1 = GF(2). The big-value")
    print(f"  carrier and the F2 substrate are the same object at different widths. Least-cost descent.")
