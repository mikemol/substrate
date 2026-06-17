#!/usr/bin/env python3
"""jea_limb_gpu.py — the byte-limb big-value carrier ON GPU: bignum arithmetic over little-endian
uint8 limb streams. Multiply = __dp4a convolution (int8 fast path); carry = PARALLEL (vectorized
scatter + ripple, no serial single-thread pass); add likewise. The carrier is the ESCALATION
TARGET: when a fixed-width (u128) combine overflows, recompute it here, exact -- escalation
DELIVERS arbitrary precision instead of merely flagging.

A value IS its little-endian byte stream (the suspended generator's materialized form): small
values cost few limbs (pay-for-size), big values grow limb-by-limb (escalate = append limbs),
and the multiply rides the GPU's int8 datapath (a*b = convolution of the limb streams).
"""
import os, time
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
import jea_core

_SRC = r'''
extern "C" __global__
void bmul_dp4a(const unsigned char* a, int La, const unsigned char* b, int Lb,
               unsigned int* col, int Lc)
{
    int k = blockIdx.x*blockDim.x + threadIdx.x; if (k >= Lc) return;
    int i_lo = max(0, k-(Lb-1)), i_hi = min(k, La-1);
    unsigned int acc = 0;
    for (int i = i_lo; i <= i_hi; i += 4) {            // 4 convolution terms per __dp4a
        unsigned int pa = 0, pb = 0;
        #pragma unroll
        for (int l = 0; l < 4; l++) {
            int ia = i+l, ib = k-(i+l);
            unsigned int av = (ia <= i_hi && ia < La) ? a[ia] : 0;     // a forward
            unsigned int bv = (ib >= 0 && ib < Lb)    ? b[ib] : 0;     // b reversed (convolution align)
            pa |= av << (8*l); pb |= bv << (8*l);
        }
        acc = __dp4a(pa, pb, acc);                     // 4 uint8 MACs, one instruction
    }
    col[k] = acc;
}
'''
_mul = jea_core.build_kernel(_SRC, "bmul_dp4a")


def to_limbs(v):
    if v == 0: return np.zeros(1, np.uint8)
    return np.frombuffer(v.to_bytes((v.bit_length()+7)//8, "little"), np.uint8).copy()
def from_limbs(arr): return int.from_bytes(bytes(arr.get().tolist() if hasattr(arr,"get") else arr.tolist()), "little")


def resolve_carry(acc):
    """PARALLEL base-256 carry over a device int-array `acc` (each entry a partial column sum).
    Every step is a vectorized cupy op (a GPU kernel) -- no serial single-thread pass. Loops until
    no entry exceeds a byte; returns trimmed uint8 limbs. (Iteration count is tiny for normal data;
    adversarial all-0xff is the O(L)-round worst case -> a carry-lookahead scan is the asymptotic fix.)"""
    acc = acc.astype(cp.uint64); it = 0
    while True:
        mx = int(acc.max())
        if mx < 256: break
        carry = acc >> 8
        acc = acc & 0xff
        acc[1:] += carry[:-1]                          # propagate one position, in parallel
        it += 1
    out = acc.astype(cp.uint8)
    nz = int((out != 0).any()) and int(cp.nonzero(out)[0][-1]) + 1 or 1
    return out[:nz], it


def gpu_mul(a_limbs, b_limbs):
    """device uint8 limbs -> (device uint8 product limbs, mul_ms, carry_iters)."""
    La, Lb = int(a_limbs.size), int(b_limbs.size); Lc = La+Lb-1
    col = cp.zeros(Lc, cp.uint32)
    cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
    _mul(((Lc+255)//256,), (256,), (a_limbs, np.int32(La), b_limbs, np.int32(Lb), col, np.int32(Lc)))
    cp.cuda.Stream.null.synchronize(); ms = (time.perf_counter()-t0)*1e3
    # parallel carry: byte d of col[k] lands at position k+d (col < 2^32 => 4 bytes)
    acc = cp.zeros(Lc+4, cp.uint64)
    for d in range(4): acc[d:d+Lc] += (col >> (8*d)) & 0xff
    out, it = resolve_carry(acc)
    return out, ms, it


def gpu_add(a_limbs, b_limbs):
    """device uint8 limbs -> device uint8 sum limbs (parallel carry)."""
    L = max(int(a_limbs.size), int(b_limbs.size)) + 1
    acc = cp.zeros(L, cp.uint64)
    acc[:a_limbs.size] += a_limbs.astype(cp.uint64)
    acc[:b_limbs.size] += b_limbs.astype(cp.uint64)
    out, _ = resolve_carry(acc)
    return out


if __name__ == "__main__":
    print("byte-limb carrier on GPU: dp4a-convolution multiply + PARALLEL carry + add + escalation target\n")

    # 1) multiply exact + the new parallel carry
    a = 7**4000; b = 11**4000
    al = cp.asarray(to_limbs(a)); bl = cp.asarray(to_limbs(b))
    gpu_mul(al, bl)
    out, ms, it = gpu_mul(al, bl)
    print(f"  1. multiply 7^4000 x 11^4000 -> {out.size} limbs: exact={from_limbs(out)==a*b}  "
          f"kernel {ms:.3f} ms, parallel-carry rounds={it} (was 1 serial O(L) pass)")

    # 2) add exact
    x, y = 11**3000, 13**3100
    s = gpu_add(cp.asarray(to_limbs(x)), cp.asarray(to_limbs(y)))
    print(f"  2. add 11^3000 + 13^3100 -> {s.size} limbs: exact={from_limbs(s)==x+y}")

    # 3) repeated squaring (big value via parallel-carry multiplies)
    xv = cp.asarray(to_limbs(3)); allok = True
    for k in range(1, 14):
        xv, _, _ = gpu_mul(xv, xv); allok &= (from_limbs(xv) == pow(3, 1<<k))
    print(f"  3. repeated squaring 3^(2^k) through 3^8192 ({xv.size} limbs): exact={allok}")

    # 4) ESCALATION DELIVERS: a u128 combine that overflows -> recompute on the byte-limb carrier, exact
    print(f"\n  4. escalation as DELIVERY (not just a flag):")
    nl, nr = 10**20, 10**20                       # product 10^40 > 2^128 (3.4e38): u128 OVERFLOWS
    u128_max = (1 << 128) - 1
    overflows = nl * nr > u128_max
    prod, _, _ = gpu_mul(cp.asarray(to_limbs(nl)), cp.asarray(to_limbs(nr)))
    exact = from_limbs(prod) == nl * nr
    print(f"     10^20 * 10^20 = 10^40: fixed-width u128 overflows = {overflows} (would flag/escalate)")
    print(f"     byte-limb carrier recomputes it: {from_limbs(prod)} == 10^40 exact = {exact}")
    print(f"     -> escalation appends limbs and DELIVERS the exact value (the spawn's wider carrier).")

    ok = (from_limbs(out)==a*b) and allok and exact
    print(f"\n  {'PASS' if ok else 'FAIL'} — byte-limb arithmetic on GPU (dp4a multiply + parallel carry + add),")
    print(f"  exact vs Python, and the escalation target delivers arbitrary precision instead of flagging.")
