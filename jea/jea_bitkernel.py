#!/usr/bin/env python3
"""jea_bitkernel.py — Δ-Ψ-bitkernel: the FUSED, BRANCHLESS bit-sliced carrier kernels. jea_graded's bs_add/bs_mul
were LOOPS of cupy ops (G launches for add, O(G^2) for mul) -- launch-bound (the navigator MEASURED the SWAR path
losing the eval-strategy dispatch for exactly this). Here the plane-loop runs INSIDE one CUDA kernel: one thread per
WORD-COLUMN (64 values), the ripple-carry / shift-and-add done sequentially per thread, PURE BITWISE -- branchless
(no data-dependent control flow -> no warp divergence). ONE launch replaces O(G) / O(G^2).

Layout: planes are (G, W) uint64, C-contiguous (plane b, word w at b*W+w); a word packs 64 values' bit b. The
arithmetic is per-value WITHIN the word (the 64 lanes carry independently via the bitwise full-adder/subtractor) --
that IS bit-slicing. recip/÷ stays a free plane-swap (gr_recip), not a kernel.

Drop-in for jea_graded.bs_add/bs_mul/bs_sub (same signatures). Witnesses ([W], __main__):
1. EXACT: fused add/mul/sub == Python over random values (incl G=1, multi-word N, a>=b for sub).
2. == the cupy-op reference (jea_graded._bs_*_ref): the fused kernel computes the identical planes.
3. [numbers] ONE launch vs O(G)/O(G^2) cupy launches; fused is faster at dispatch scale (-> SWAR can win).
"""
import os, sys, time
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_core   # Π10: the leaf home for the shared limb helpers (pad/trim/lh)

_SRC = r'''
extern "C" __global__ void bs_add_k(const unsigned long long* A, const unsigned long long* B,
                                    unsigned long long* out, int G, int W) {
  int w = blockIdx.x*blockDim.x + threadIdx.x; if (w >= W) return;
  unsigned long long carry = 0;                                   // per-value carry (64 lanes, branchless full-adder)
  for (int b = 0; b < G; b++) {
    long long o=(long long)b*W+w; unsigned long long a=A[o], bb=B[o];
    out[o] = a ^ bb ^ carry; carry = (a & bb) | (carry & (a ^ bb));
  }
  out[(long long)G*W + w] = carry;
}
extern "C" __global__ void bs_sub_k(const unsigned long long* A, const unsigned long long* B,
                                    unsigned long long* out, unsigned long long* bor, int G, int W) {
  int w = blockIdx.x*blockDim.x + threadIdx.x; if (w >= W) return;
  unsigned long long F=0xFFFFFFFFFFFFFFFFULL, b_=0;               // ripple-BORROW, branchless full-subtractor
  for (int b = 0; b < G; b++) {
    long long o=(long long)b*W+w; unsigned long long a=A[o], bb=B[o];
    out[o] = a ^ bb ^ b_; b_ = ((a^F) & bb) | (((a^bb)^F) & b_);
  }
  bor[w] = b_;                                                    // per-value borrow_out (1 = A<B)
}
extern "C" __global__ void bs_mul_k(const unsigned long long* A, int Ga, const unsigned long long* B, int Gb,
                                    unsigned long long* out, int W) {
  int w = blockIdx.x*blockDim.x + threadIdx.x; if (w >= W) return;
  int Gc = Ga + Gb;
  for (int b = 0; b < Gc; b++) out[(long long)b*W + w] = 0;       // this thread owns column w across all planes
  for (int c = 0; c < Gb; c++) {
    unsigned long long mask = B[(long long)c*W + w], carry = 0;   // per-value bit-c of B (shift-and-add)
    for (int i = 0; i < Ga; i++) {
      long long o=(long long)(c+i)*W+w; unsigned long long partial = A[(long long)i*W+w] & mask, cur = out[o];
      out[o] = cur ^ partial ^ carry; carry = (cur & partial) | (carry & (cur ^ partial));
    }
    for (int p = c+Ga; p < Gc; p++) {                            # ripple the residual carry up (fixed-length, branchless)
      long long o=(long long)p*W+w; unsigned long long cur = out[o]; out[o] = cur ^ carry; carry = cur & carry;
    }
  }
}
'''.replace("#", "//")
assert _SRC.isascii(), "kernel source must be ASCII"
_kadd = cp.RawKernel(_SRC, "bs_add_k"); _ksub = cp.RawKernel(_SRC, "bs_sub_k"); _kmul = cp.RawKernel(_SRC, "bs_mul_k")
_THR = 128
def _grid(W): return ((W + _THR - 1)//_THR,)
_pad = jea_core.pad   # Π10: shared limb-pad lives in jea_core (the leaf both bitkernel & graded reach without a cycle)


def bs_add(A, B):
    """Fused bit-sliced add: A,B (G,W) -> (max(Ga,Gb)+1, W). ONE kernel launch (the ripple-carry is inside)."""
    G = max(A.shape[0], B.shape[0]); W = A.shape[1]; A = _pad(A, G); B = _pad(B, G)
    out = cp.empty((G+1, W), cp.uint64); _kadd(_grid(W), (_THR,), (A, B, out, np.int32(G), np.int32(W))); return out

def bs_sub(A, B):
    """Fused bit-sliced ripple-borrow subtract: (A-B mod 2^G, per-value borrow). ONE launch."""
    G = max(A.shape[0], B.shape[0]); W = A.shape[1]; A = _pad(A, G); B = _pad(B, G)
    out = cp.empty((G, W), cp.uint64); bor = cp.empty(W, cp.uint64)
    _ksub(_grid(W), (_THR,), (A, B, out, bor, np.int32(G), np.int32(W))); return out, bor

def bs_mul(A, B):
    """Fused bit-sliced shift-and-add multiply: A (Ga) x B (Gb) -> (Ga+Gb, W). ONE launch (was O(Ga*Gb) cupy ops)."""
    Ga, W = A.shape; Gb = B.shape[0]; out = cp.empty((Ga+Gb, W), cp.uint64)
    _kmul(_grid(W), (_THR,), (A, np.int32(Ga), B, np.int32(Gb), out, np.int32(W))); return out


if __name__ == "__main__":
    print("jea_bitkernel: the FUSED branchless bit-sliced carrier -- ONE kernel launch per op (was O(G)/O(G^2) cupy ops)\n")
    import jea_graded as G
    rng = np.random.default_rng(13)
    grades = [int(g) for g in rng.integers(1, 8, size=140)] + [int(g) for g in rng.integers(8, 45, size=60)]
    A = [int(rng.integers(0, 1<<g)) for g in grades]; B = [int(rng.integers(0, 1<<g)) for g in grades]; N = len(A)
    pA, _ = G.to_bitsliced(A); pB, _ = G.to_bitsliced(B)

    add_f = G.from_bitsliced(bs_add(pA, pB), N); mul_f = G.from_bitsliced(bs_mul(pA, pB), N)
    hi = [max(a, b) for a, b in zip(A, B)]; lo = [min(a, b) for a, b in zip(A, B)]
    pH, _ = G.to_bitsliced(hi); pL, _ = G.to_bitsliced(lo); sd, bor = bs_sub(pH, pL); sub_f = G.from_bitsliced(sd, N)
    w1 = (add_f == [a+b for a, b in zip(A, B)]) and (mul_f == [a*b for a, b in zip(A, B)]) \
         and (sub_f == [h-l for h, l in zip(hi, lo)]) and int(bor.sum()) == 0
    print(f"  W1  EXACT vs Python ({N} values): fused add/mul/sub all correct (incl multi-word, a>=b sub): {w1}")

    # W2: == the cupy-op reference in jea_graded (identical planes)
    ra = G.from_bitsliced(G._bs_add_ref(pA, pB), N); rm = G.from_bitsliced(G._bs_mul_ref(pA, pB), N)
    w2 = (add_f == ra) and (mul_f == rm)
    print(f"  W2  == cupy-op reference (jea_graded._bs_*_ref): fused planes == cupy planes: {w2}")

    # W3 [numbers]: ONE launch vs O(G)/O(G^2) cupy ops; fused faster at dispatch scale (W=64 words, G~mixed)
    Nd = 4096; gd = [int(rng.integers(1, 40)) for _ in range(Nd)]
    Ad = [int(rng.integers(0, 1<<g)) for g in gd]; Bd = [int(rng.integers(0, 1<<g)) for g in gd]
    pAd, _ = G.to_bitsliced(Ad); pBd, _ = G.to_bitsliced(Bd); Gd = pAd.shape[0]
    bs_mul(pAd, pBd); G._bs_mul_ref(pAd, pBd); cp.cuda.Stream.null.synchronize()           # warm
    t0 = time.perf_counter(); [bs_mul(pAd, pBd) for _ in range(5)]; cp.cuda.Stream.null.synchronize(); tf = (time.perf_counter()-t0)/5
    t0 = time.perf_counter(); [G._bs_mul_ref(pAd, pBd) for _ in range(5)]; cp.cuda.Stream.null.synchronize(); tc = (time.perf_counter()-t0)/5
    w3 = tf < tc
    print(f"  W3  [numbers] bs_mul on N={Nd},G={Gd}: fused = {tf*1e3:.2f} ms (1 launch) vs cupy-op = {tc*1e3:.2f} ms "
          f"(~{Gd*Gd} launches) -- {tc/max(tf,1e-9):.0f}x faster: {w3}")

    ok = w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — the fused branchless bit-sliced kernel: ONE launch per add/mul/sub (the")
    print(f"  plane-loop is inside the kernel, one thread per word-column, pure bitwise = no warp divergence). Drop-in")
    print(f"  for jea_graded.bs_add/bs_mul/bs_sub -> the SWAR carrier is no longer launch-bound (the dispatch can pick it).")
