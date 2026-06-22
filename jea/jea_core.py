#!/usr/bin/env python3
"""jea_core.py — the STRICT shared structure the jea_generator_* scripts instantiate.

STRUCTURAL STRICTIFICATION. Through increments (1)-(6) the claim was "one generator primitive,
different step_fn" — but each script physically copy-pasted the control law, the residency
invariant, and the compile boilerplate, so the claimed unity was NARRATIVE, not structural
(a retrospective finding: the central claim of the arc was asserted in prose, never compiled).
This module makes it strict: the shared structure lives HERE, once, and every variant imports
it. Each jea_generator_*.py then differs ONLY in its step_fn kernel body — which is the actual
content of "one primitive, different step_fn", now enforced by construction.

Shared pieces:
  * CTRL_CUDA   — the exact-rational control law (numK + relax_q), CUDA source, defined once.
  * Q128_CUDA   — the u128 lane helpers (ld/st) for the 128-bit carrier.
  * build_kernel— compile through the ASCII GATE (the G9 escalation of the em-dash/ℚ/->/=>
                  NVRTC failure that recurred 4x: refuse non-ASCII device source BEFORE compile,
                  with a precise pointer, instead of a cryptic UnicodeEncodeError deep in cupy).
  * residency   — the resident_blocks >= launched_blocks liveness invariant, measured.
  * relax_q_ref — the control law as a Python reference (the bisimulation oracle), the same
                  decision the CUDA relax_q makes (jea_nedge_model's Fraction plant model is the
                  non-collapsed form of this integer law; they were proven equal in increment 2).
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")          # cupy NVRTC + ncu header resolution
import cupy as cp

# --- the exact-rational control law (shared CUDA source) ---------------------
# Plant-model totals share a common denominator (25600), so total(A)<total(B) is an EXACT
# integer numerator compare (no division, no float): numK = passes * (421376 + max(548*K,66304)).
CTRL_CUDA = r'''
__device__ __forceinline__ long long numK(int K,int md){
    long long p=(md+K-1)/K; long long alu=(548LL*K>66304LL)?548LL*K:66304LL; return p*(421376LL+alu); }
__device__ __forceinline__ int relax_q(int K,int md){
    int d=K/2; if(d<1)d=1; int u=K*2; if(u>256)u=256;
    long long nK=numK(K,md),nd=numK(d,md),nu=numK(u,md); return (nd<nK)?d:(nu<nK)?u:K; }
'''

# --- u128 lane helpers (shared CUDA source, the 128-bit carrier) -------------
Q128_CUDA = r'''
typedef unsigned long long u64; typedef unsigned __int128 u128;
__device__ __forceinline__ u128 ld(const u64* lo,const u64* hi,int i){ return ((u128)hi[i]<<64)|lo[i]; }
__device__ __forceinline__ void st(u64* lo,u64* hi,int i,u128 v){ lo[i]=(u64)v; hi[i]=(u64)(v>>64); }
'''


def lh(vals):
    """Host-side limb split: ints -> (lo, hi) cupy uint64 arrays, the (lo,hi) pair the device `ld`/`st`
    above pack/unpack. The shared leaf-loader the cooperative generators use; promoted here from the
    byte-identical jea_generator_{strat,unified}._lh (Φ3 fold) since both already import jea_core."""
    M = (1 << 64) - 1
    vals = [int(v) for v in vals]
    return cp.asarray([v & M for v in vals], cp.uint64), cp.asarray([(v >> 64) & M for v in vals], cp.uint64)


def pad(A, G):
    """Zero-pad a (rows, W) uint64 limb matrix up to G rows (no-op if already ≥ G). The shared leaf
    helper promoted here from the byte-identical jea_bitkernel._pad / jea_graded._pad (Π10); it could
    not fold bitkernel→graded (jea_graded imports jea_bitkernel, so that import is local to break the
    cycle) — jea_core is the leaf both reach without a cycle."""
    return A if A.shape[0] >= G else cp.concatenate([A, cp.zeros((G - A.shape[0], A.shape[1]), cp.uint64)])


def trim(arr):
    """Trailing-zero-trim a little-endian uint8 limb array, keeping ≥ 1 element. Promoted here from the
    same-semantics jea_carrier_base._trim / jea_resident._trim (Π10)."""
    nz = cp.nonzero(arr)[0]
    return arr[:int(nz[-1]) + 1] if nz.size else arr[:1]


def build_kernel(src, name, int128=False):
    """Compile a RawKernel through the ASCII GATE. CUDA source MUST be ASCII — em-dash, the
    rational symbol, middot, double-arrow etc. in NVRTC comments fail with a cryptic
    UnicodeEncodeError deep inside cupy (this class recurred 4x in one session). Assert it here,
    before compile, with a precise line/col/codepoint pointer. Keep unicode in Python strings."""
    if not src.isascii():
        for ln_no, line in enumerate(src.splitlines(), 1):
            for col, ch in enumerate(line, 1):
                if ord(ch) > 127:
                    raise ValueError(
                        f"CUDA source for '{name}' is non-ASCII at line {ln_no} col {col}: "
                        f"U+{ord(ch):04x} {ch!r}. NVRTC needs ASCII in device source — "
                        f"use ASCII in device comments (unicode is fine in Python strings).")
    opts = ('--device-int128',) if int128 else ()
    return cp.RawKernel(src, name, options=opts)


def residency(kernel, block_threads, smem_bytes=0):
    """resident_blocks >= launched_blocks is a SEMANTIC requirement for the cyclic
    controller<->worker comm graph (a descheduled participant breaks liveness), not an
    optimization. Measured from the COMPILED kernel's register footprint. Ada sm_89 limits."""
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]
    REGS_SM, THREADS_SM, SMEM_SM = 65536, 1536, 101376
    regs = kernel.num_regs
    per_sm = max(0, min(REGS_SM // (max(regs, 1) * block_threads),
                        THREADS_SM // block_threads,
                        (SMEM_SM // smem_bytes) if smem_bytes else 10**9))
    return per_sm, per_sm * nsm, nsm, regs


def relax_q_ref(K, md):
    """Python reference for the control law — bit-identical to the CUDA relax_q (same
    common-denominator integer compare). The bisimulation oracle for the on-device controller."""
    def numK(K, md):
        p = -(-md // K); return p * (421376 + max(548 * K, 66304))
    d = max(1, K // 2); u = min(256, K * 2)
    nK, nd, nu = numK(K, md), numK(d, md), numK(u, md)
    return d if nd < nK else u if nu < nK else K


def num_sms():
    return cp.cuda.Device().attributes["MultiProcessorCount"]
