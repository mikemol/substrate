#!/usr/bin/env python3
"""jea_limb_gpu.py — the byte-limb big-value carrier ON GPU: bignum multiply as a __dp4a
convolution over the limb streams (the int8 fast path), exact, vs Python int.

A value is a little-endian uint8 limb stream (the suspended generator's materialized form). The
product a*b is the CONVOLUTION of the two limb streams: col[k] = sum_{i+j=k} a[i]*b[j], then a
carry pass. The convolution maps onto __dp4a: pack a[i..i+3] forward and b[k-i..k-i-3] reversed
into two u32 words; one __dp4a accumulates four convolution terms a[i+l]*b[k-i-l]. So the
big-value multiply runs on the GPU's int8 datapath (verified __dp4a works on sm_89), columns in
parallel, carry in one O(L) pass. Pay-for-what-you-use (limbs = significant bytes); escalate =
append limbs. GMP ropes eager limbs together; here the carrier IS the byte stream and multiply is
the convolution on the int8 SIMD path.
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

extern "C" __global__
void carry(const unsigned int* col, int Lc, unsigned char* out, int Lout)
{
    if (threadIdx.x || blockIdx.x) return;             // serial carry pass, O(L)
    unsigned long long c = 0;
    for (int t = 0; t < Lout; t++) {
        c += (t < Lc) ? (unsigned long long)col[t] : 0ULL;
        out[t] = (unsigned char)(c & 0xff); c >>= 8;
    }
}
'''
_mul = jea_core.build_kernel(_SRC, "bmul_dp4a")
_carry = cp.RawKernel(_SRC, "carry")


def to_limbs(v):
    if v == 0: return np.zeros(1, np.uint8)
    return np.frombuffer(v.to_bytes((v.bit_length()+7)//8, "little"), np.uint8).copy()

def from_limbs(arr):
    return int.from_bytes(bytes(arr.tolist()), "little")


def gpu_mul(a_limbs, b_limbs):
    """a_limbs, b_limbs: device uint8 arrays. Returns (device out uint8 limbs, mul_kernel_ms)."""
    La, Lb = int(a_limbs.size), int(b_limbs.size); Lc = La+Lb-1; Lout = La+Lb
    col = cp.zeros(Lc, cp.uint32); out = cp.zeros(Lout, cp.uint8)
    cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
    _mul(((Lc+255)//256,), (256,), (a_limbs, np.int32(La), b_limbs, np.int32(Lb), col, np.int32(Lc)))
    cp.cuda.Stream.null.synchronize(); ms = (time.perf_counter()-t0)*1e3
    _carry((1,), (1,), (col, np.int32(Lc), out, np.int32(Lout)))
    cp.cuda.Stream.null.synchronize()
    return out, ms


if __name__ == "__main__":
    print("byte-limb big-value carrier on GPU: multiply = __dp4a convolution over limb streams\n")

    # 1) exactness on a big single multiply (the spec's operands)
    a = 7**4000; b = 11**4000
    al = cp.asarray(to_limbs(a)); bl = cp.asarray(to_limbs(b))
    gpu_mul(al, bl)                                    # warm
    out, ms = gpu_mul(al, bl)
    got = from_limbs(out.get()); ok = (got == a*b)
    print(f"  1. 7^4000 ({al.size} limbs) x 11^4000 ({bl.size} limbs) -> {out.size} limbs")
    print(f"     == Python a*b (exact): {ok}   multiply kernel {ms:.3f} ms")

    # 2) big VALUE by repeated squaring on GPU (the carrier grows through dp4a multiplies)
    print(f"\n  2. repeated squaring on GPU (3^(2^k)): carrier grows, each square = a dp4a convolution")
    x = cp.asarray(to_limbs(3)); allok = True
    for k in range(1, 14):
        x, _ = gpu_mul(x, x)                           # x <- x*x
        ref = pow(3, 1 << k)
        ok = (from_limbs(x.get()) == ref); allok &= ok
        if k in (4, 8, 12, 13):
            print(f"     after {k:2d} squarings: 3^{1<<k} = {x.size:>4} limbs (~{ref.bit_length()} bits)  exact={ok}")

    # 3) total dp4a throughput on the big multiply
    La = al.size; Lb = bl.size; macs = La*Lb
    print(f"\n  3. the {La}x{Lb} multiply = {macs/1e6:.1f}M uint8 MACs via __dp4a (int8 datapath), {ms:.3f} ms"
          f" = {macs/ms/1e6:.0f}M MAC/ms")
    print(f"\n  {'PASS' if ok and allok else 'FAIL'} — big values carried as byte-limb streams (pay-for-size),"
          f" multiplied by")
    print(f"  __dp4a convolution on the int8 fast path, exact vs Python. The escalation-spawn's wider carrier.")
