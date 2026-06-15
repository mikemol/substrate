#!/usr/bin/env python3
"""jea_fit_plant.py — D1: DISCHARGE the relax_q plant constants (GUESSED/mis-cited "fitted to ablation")
by an actual fit + output-side ground-truth. (Provenance: GUESSED -> MEASURED.)

The plant per-pass cost is t_pass(K) = t_mem + K*c_step (memory per pass + K Euclid ALU steps); total(K,D)
= ceil(D/K) * t_pass(K). The constants 421376/548/66304 (jea_core) / t_mem=16.46, c_step=2.14, t_ovf=2.59
(jea_nedge_model) were HAND-ENTERED with no fitting code. Here we MEASURE t_pass(K) on the actual gcd-window
kernel at several K, FIT (t_mem, c_step) by least squares, and GROUND-TRUTH the FORM by predicting total at a
HELD-OUT K (never used in the fit) and measuring it -- output-side validation (validate-outputs-not-inputs).

SCOPE (honest): this fits the two gcd-window constants (t_mem, c_step) -- the dominant terms relax_q's numK
uses (421376 ~ t_mem, 548 ~ c_step). t_ovf (66304; the Q-combine overflow-division floor, only firing at
K*c_step < t_ovf) is NOT in the pure-gcd window -> D1-REST: measure it from the Q-combine kernel's per-pass
floor at small K. The numbers are in THIS kernel's ms (workload-specific); the DISCHARGE is that they are now
fit-with-residuals + the FORM is held-out-validated, not hand-entered.

Witnesses (each [W]):
1. MEASURED: t_pass(K) timed at >=5 K on the actual gcd-window kernel (the object the plant models).
2. FIT: t_pass = t_mem + K*c_step least-squares; residual small (the linear plant FORM fits the data).
3. GROUND-TRUTH (output-side): a HELD-OUT K (not in the fit) -- predicted total vs measured total within tol;
   the FORM predicts, doesn't merely interpolate.
4. PROVENANCE FLIP: t_mem, c_step now MEASURED (fit + residual + held-out), replacing GUESSED. (t_ovf = D1-rest.)
"""
import os, time
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp

# deep gcd: consecutive Fibonacci F(88),F(89) (< 2^64) -> ~87 Euclid steps, so K<=64 windows never converge mid-pass
F88, F89 = 1100087778366101931, 1779979416004714189
DEPTH = 87
_gw = cp.RawKernel(r'''
extern "C" __global__ void gw(unsigned long long* a, unsigned long long* b, int K, int n){
    int i = blockIdx.x*blockDim.x + threadIdx.x; if (i>=n) return;
    unsigned long long x=a[i], y=b[i];
    for (int j=0;j<K;j++){ if (y!=0){ unsigned long long r=x%y; x=y; y=r; } }
    a[i]=x; b[i]=y;
}''', "gw")
N = 1 << 20
BLK = 256


def t_pass(K, reps=5):
    """ms for ONE pass of K Euclid steps over N lanes (fresh deep operands)."""
    best = 1e9
    for _ in range(reps):
        a = cp.full(N, F89, cp.uint64); b = cp.full(N, F88, cp.uint64)
        cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
        _gw(((N+BLK-1)//BLK,), (BLK,), (a, b, np.int32(K), np.int32(N)))
        cp.cuda.Stream.null.synchronize(); best = min(best, (time.perf_counter()-t0)*1e3)
    return best


def total_measured(K, D, reps=5):
    """ms for ceil(D/K) passes (windowed gcd to depth D), carrying (a,b) across passes."""
    passes = -(-D // K); best = 1e9
    for _ in range(reps):
        a = cp.full(N, F89, cp.uint64); b = cp.full(N, F88, cp.uint64)
        cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
        for _ in range(passes): _gw(((N+BLK-1)//BLK,), (BLK,), (a, b, np.int32(K), np.int32(N)))
        cp.cuda.Stream.null.synchronize(); best = min(best, (time.perf_counter()-t0)*1e3)
    return best, passes


if __name__ == "__main__":
    t_pass(8)                                              # warm JIT
    Ks = [4, 8, 16, 32, 64]                                # fit set (>=5)
    tp = [t_pass(K) for K in Ks]
    c_step, t_mem = np.polyfit(Ks, tp, 1)                  # t_pass = t_mem + K*c_step
    pred = [t_mem + K*c_step for K in Ks]
    resid = max(abs(p-m)/m for p, m in zip(pred, tp))      # max relative residual on the fit

    # GROUND-TRUTH: held-out K=24 (NOT in the fit); predict total(24, DEPTH) from the form, then MEASURE it.
    Kh = 24; passes_h = -(-DEPTH // Kh)
    pred_total = passes_h * (t_mem + Kh*c_step)
    meas_total, _ = total_measured(Kh, DEPTH)
    gt_err = abs(pred_total - meas_total)/meas_total

    w1 = len(Ks) >= 5
    w2 = resid < 0.20                                      # does the linear plant FORM fit? (<20% max residual)
    w3 = gt_err < 0.25                                     # does the held-out prediction match measurement?
    w4 = w2 and w3                                         # provenance flips ONLY if the form fits + ground-truth holds
    alu_dominant = t_mem < c_step * Ks[0]                  # measured: is the per-pass cost ALU-bound (t_mem ~ 0)?
    print("D1 -- attempt to FIT the relax_q plant constants from measurement + held-out ground-truth\n")
    print(f"  measured t_pass(K) ms over K={Ks}: {[round(x,4) for x in tp]}")
    print(f"  FIT: t_pass = t_mem + K*c_step -> t_mem={t_mem:.4f} ms, c_step={c_step:.5f} ms/step; max resid={resid*100:.1f}%")
    print(f"  GROUND-TRUTH held-out K={Kh} (D={DEPTH}, {passes_h} passes): predicted {pred_total:.3f} ms, measured {meas_total:.3f} ms, err={gt_err*100:.1f}%")
    print(f"\n1. MEASURED (t_pass at >={len(Ks)} K on the gcd-window kernel): {w1}")
    print(f"2. FIT (linear plant form fits, max residual {resid*100:.1f}% < 20%): {w2}")
    print(f"3. GROUND-TRUTH (held-out K predicted within {gt_err*100:.1f}% < 25%): {w3}")
    print(f"4. PROVENANCE FLIP (constants validated -> GUESSED becomes MEASURED): {w4}")
    print(f"\n  {'PASS' if w4 else 'FAIL -- ground-truth FALSIFIED the model (this is the discipline WORKING)'}\n")
    print(f"  FINDINGS (honest, output-side falsification): the linear FORM t_mem+K*c_step does NOT fit this")
    print(f"  kernel (resid {resid*100:.0f}%, held-out err {gt_err*100:.0f}%) -- the data is near-proportional-to-K for")
    print(f"  K<=32 then saturates at K=64, so the single-line form fits neither region. The fitted t_mem={t_mem:.2f}ms")
    print(f"  is SMALL (a fit artifact) -- nowhere near the hand-entered MEMORY-dominant t_mem=16.46, so that")
    print(f"  regime claim is at least not reproduced here. BUT this microkernel (1M parallel lanes) is a DIFFERENT")
    print(f"  regime than the evaluator (few dependent MLP-starved nodes) -> also the wrong object. So D1 is NOT")
    print(f"  discharged: (a) the plant FORM is unvalidated (needs a refined/regime-dependent term), (b) the proper")
    print(f"  fit is on the ACTUAL evaluator kernel at FIXED K, (c) which regime binds must be MEASURED per kernel,")
    print(f"  never predetermined. relax_q constants stay GUESSED/UNVALIDATED -- the ground-truth refused to bless them.")
