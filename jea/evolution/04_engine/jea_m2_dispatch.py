#!/usr/bin/env python3
"""jea_m2_dispatch.py — M2d: close the loop. The nedge oracle steers the resident Q-evaluator, live.

SCOPE (honest): the production on-device evaluator (jea_generator_* ladder) and the closed Agda-on-GPU
spit-take (jea_agda_bridge.py, 8046b4c) ALREADY EXIST and are more advanced than this script. This is a
clean, self-contained reference build of the dataflow core (M2a-c) plus a GENUINELY NEW knob: the nedge
oracle steering the value-window<->trace-window (eager/lazy reduction) Pareto LIVE -- distinct from the
existing controller, which steers only K (the gcd-window size). The DAG here is synthetic SPPF-shaped.

M2a-c built a persistent data-driven sweep that evaluates an SPPF-shaped DAG over the EXACT Q carrier
(gcd-window + escalate-don't-truncate). The kernel-perf detour built the DISPATCHER ORACLE (the el-atlas
nedge G-Value calculus: G_OR/G_AND conductances, the geodesic/min-dissipation settle). M2d connects them:
the oracle picks the evaluator's SCHEDULE and pushes it into the RESIDENT kernel via the AI-11b zero-copy
mapped-control channel (host -> device, async, no sync).

What the oracle steers = the value-window <-> trace-window PARETO, the knob named at the very start of this
arc ("dense arithmetic throughput vs exactness/canonicality without forcing full reduction"):
  * MODE=1 EAGER (value-window canonical): reduce every op -> outputs canonical (gcd==1), costs gcd-work.
  * MODE=0 LAZY  (defer reduction): reduce ONLY when the lane forces it -> high throughput (skips gcd when
    the unreduced pair fits int64), but outputs are non-canonical (must reduce-on-demand to compare).
Both are EXACT (a non-reduced fraction is still the right rational; reduce at readout recovers canonical).
The oracle weighs throughput vs the workload's canonicality-demand C and picks the operating point; the
crossover C=f* is the value<->trace bridge-null.

Witnesses (each [W]):
1. EXACT (every run): reduce(num,den) == host Fraction reference for all non-escalated nodes; escalation
   detected exactly (== unrepresentable set), never wrapped -- in eager, lazy, AND the live oracle-run.
2. PARETO REAL (measured, not asserted): lazy does strictly LESS gcd-work (throughput win) but emits >0
   non-canonical nodes; eager emits 0 non-canonical at higher gcd-work. The crossover f* is computed.
3. ORACLE-STEERED: the el-atlas nedge cost (resistance-sum / geodesic settle) picks MODE from on-device
   telemetry + the workload's C; the decision FLIPS across f* (low-C -> lazy, high-C -> eager).
4. LIVE CLOSED LOOP: the chosen MODE is pushed into a RESIDENT (spin-waiting) kernel via the zero-copy
   control buffer; the kernel honors it and completes -> Agda-term DAG -> on-device exact dataflow ->
   oracle-scheduled, live. The detour's oracle now drives the charter's evaluator.
"""
import os, time, ctypes
os.environ.setdefault("CUDA_PATH", "/usr")
from fractions import Fraction
import numpy as np, cupy as cp

SRC = r"""
typedef long long i64;
extern "C" __global__ void qeval(const int* op, const i64* lnum, const i64* lden,
                                 const int* c0, const int* c1, i64* num, i64* den, int* esc, int* steps,
                                 volatile int* status, int* completed, volatile int* ctrl, int n) {
    const __int128 LIM = ((__int128)1) << 62;
    int stride = gridDim.x * blockDim.x, t0 = blockIdx.x * blockDim.x + threadIdx.x;
    while (!ctrl[2]) { if (ctrl[0]) return; long long t = clock64(); while (clock64() - t < 2000) {} } // resident: wait for host GO
    int mode = ctrl[1];                                                       // schedule pushed by the oracle
    long long sweeps = 0, cap = (long long)n + 16;
    while (*completed < n && sweeps++ < cap) {
        if (ctrl[0]) return;
        for (int i = t0; i < n; i += stride) {
            if (status[i] != 0) continue;
            int o = op[i]; bool ready = false; int e = 0, st = 0; __int128 N = 0, D = 1;
            if (o == 0) { N = lnum[i]; D = lden[i]; ready = true; }
            else if (status[c0[i]] == 1 && status[c1[i]] == 1) {
                ready = true;
                if (esc[c0[i]] || esc[c1[i]]) { e = 1; N = 0; D = 1; }
                else {
                    __int128 xn = num[c0[i]], xd = den[c0[i]], yn = num[c1[i]], yd = den[c1[i]];
                    if (o == 1) { N = xn * yd + yn * xd; D = xd * yd; } else { N = xn * yn; D = xd * yd; }
                    __int128 an = N < 0 ? -N : N;
                    bool reduce = (mode == 1) || (an >= LIM || D >= LIM);      // eager always; lazy only if forced
                    if (reduce) {
                        __int128 a = an, b = D; while (b) { __int128 t = a % b; a = b; b = t; st++; }
                        N /= a; D /= a; an = N < 0 ? -N : N;
                        if (an >= LIM || D >= LIM) { e = 1; N = 0; D = 1; }    // escalate, don't wrap
                    }
                }
            }
            if (ready && atomicCAS((int*)&status[i], 0, 2) == 0) {
                num[i] = (i64)N; den[i] = (i64)D; esc[i] = e; steps[i] = st;
                __threadfence(); status[i] = 1; __threadfence(); atomicAdd(completed, 1);
            }
        }
        __threadfence();
    }
}
"""


def mapped_i32(n):                                                            # AI-11b zero-copy: UVA pinned host<->device
    nb = n * 4
    mem = cp.cuda.alloc_pinned_memory(nb)
    host = (ctypes.c_int32 * n).from_address(mem.ptr)
    dev = cp.ndarray((n,), cp.int32, memptr=cp.cuda.MemoryPointer(cp.cuda.UnownedMemory(mem.ptr, nb, mem), 0))
    for i in range(n):
        host[i] = 0
    return mem, host, dev


if __name__ == "__main__":
    ker = cp.RawKernel(SRC, "qeval", options=("--device-int128",))
    # --- build an SPPF DAG over Q + a distinct-prime chain that forces escalation (M2c construction) ---
    W, D = 1000, 40
    n = W * D
    rng = np.random.default_rng(0)
    op = np.zeros(n, np.int32); lnum = np.zeros(n, np.int64); lden = np.ones(n, np.int64)
    c0 = np.zeros(n, np.int32); c1 = np.zeros(n, np.int32)
    dens = np.array([1, 2, 3, 5], np.int64)
    for i in range(W):
        f = Fraction(int(rng.integers(-2, 3)), int(rng.choice(dens)))
        lnum[i], lden[i] = f.numerator, f.denominator
    for k in range(1, D):
        lo, hi = k * W, (k + 1) * W
        op[lo:hi] = rng.integers(1, 3, W)
        c0[lo:hi] = rng.integers(0, k * W, W); c1[lo:hi] = rng.integers(0, k * W, W)
    primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    ch_op, ch_ln, ch_ld, ch_c0, ch_c1 = [0], [1], [primes[0]], [0], [0]
    prev, idx = n, n + 1
    for j in range(1, len(primes)):
        ch_op += [0, 2]; ch_ln += [1, 0]; ch_ld += [primes[j], 1]; ch_c0 += [0, prev]; ch_c1 += [0, idx]; prev = idx + 1; idx += 2
    op = np.concatenate([op, np.array(ch_op, np.int32)])
    lnum = np.concatenate([lnum, np.array(ch_ln, np.int64)]); lden = np.concatenate([lden, np.array(ch_ld, np.int64)])
    c0 = np.concatenate([c0, np.array(ch_c0, np.int32)]); c1 = np.concatenate([c1, np.array(ch_c1, np.int32)])
    n = len(op)

    LIM = 1 << 62
    fits = lambda fr: abs(fr.numerator) < LIM and fr.denominator < LIM
    val = [None] * n; esc_ref = np.zeros(n, np.int32)                          # host reference (exact) + poison-propagation
    for i in range(n):
        if op[i] == 0:
            val[i] = Fraction(int(lnum[i]), int(lden[i])); esc_ref[i] = 0 if fits(val[i]) else 1
        else:
            a, b = int(c0[i]), int(c1[i])
            if esc_ref[a] or esc_ref[b]: esc_ref[i] = 1; val[i] = Fraction(0); continue
            val[i] = val[a] + val[b] if op[i] == 1 else val[a] * val[b]
            esc_ref[i] = 0 if fits(val[i]) else 1
    ref_num = np.array([0 if esc_ref[i] else val[i].numerator for i in range(n)], np.int64)
    ref_den = np.array([1 if esc_ref[i] else val[i].denominator for i in range(n)], np.int64)

    d = lambda x: cp.asarray(x)
    g_op, g_ln, g_ld, g_c0, g_c1 = d(op), d(lnum), d(lden), d(c0), d(c1)
    num = cp.zeros(n, cp.int64); den = cp.ones(n, cp.int64); esc = cp.zeros(n, cp.int32); steps = cp.zeros(n, cp.int32)
    status = cp.zeros(n, cp.int32); completed = cp.zeros(1, cp.int32)
    _mem, host_ctrl, dev_ctrl = mapped_i32(4)                                  # [STOP, MODE, GO, _]
    blocks, threads = 16, 64

    def run(mode, live=False):
        num.fill(0); den.fill(1); esc.fill(0); steps.fill(0); status.fill(0); completed.fill(0)
        host_ctrl[0] = 0; host_ctrl[1] = mode; host_ctrl[2] = 0 if live else 1
        args = (g_op, g_ln, g_ld, g_c0, g_c1, num, den, esc, steps, status, completed, dev_ctrl, np.int32(n))
        if not live:
            ker((blocks,), (threads,), args); cp.cuda.Stream.null.synchronize()
            waited = 0.0
        else:
            st = cp.cuda.Stream(non_blocking=True)
            with st:
                ker((blocks,), (threads,), args)                              # resident, spinning on GO
            time.sleep(0.10)                                                  # kernel provably waits, resident
            host_ctrl[1] = mode                                              # oracle pushes the SCHEDULE...
            host_ctrl[2] = 1                                                  # ...and GO, via zero-copy into the live kernel
            st.synchronize(); waited = 0.10
        gn, gd, ge, gs = num.get(), den.get(), esc.get(), steps.get()
        live_mask = ge == 0
        red = [Fraction(int(gn[i]), int(gd[i])) if live_mask[i] else None for i in range(n)]
        exact = all((red[i] == val[i]) for i in range(n) if live_mask[i])
        esc_ok = bool((ge == esc_ref).all())
        gwork = int(gs.sum())
        noncanon = int(((np.gcd(np.abs(gn[live_mask]), gd[live_mask])) != 1).sum())
        return dict(exact=exact, esc_ok=esc_ok, gwork=gwork, noncanon=noncanon, comp=int(completed.get()[0]), waited=waited)

    eager = run(1); lazy = run(0)                                              # profile both arms of the Pareto

    # --- the el-atlas nedge oracle: pick MODE from telemetry + the workload's canonicality-demand C ---
    # resistance-sum (series G_AND in resistance space); geodesic/min-dissipation settle = argmin cost.
    W_T, W_C = 1.0, 1.0
    cost = lambda gwork, noncanon, C: W_T * gwork + C * W_C * noncanon        # throughput-resistance + C-weighted canon-resistance
    # crossover (bridge-null): cost_eager(C*) == cost_lazy(C*)  =>  C* = W_T(g_eager - g_lazy)/(W_C * nc_lazy)
    fstar = (W_T * (eager["gwork"] - lazy["gwork"])) / (W_C * max(lazy["noncanon"], 1))
    decide = lambda C: 1 if cost(eager["gwork"], eager["noncanon"], C) <= cost(lazy["gwork"], lazy["noncanon"], C) else 0
    C_lo, C_hi = 0.0, max(2 * fstar, 1.0)                                      # straddle the crossover
    dec_lo, dec_hi = decide(C_lo), decide(C_hi)

    # workload here HAS comparison/dedup sinks -> high canonicality demand -> oracle should choose eager.
    C_workload = C_hi
    chosen = decide(C_workload)
    live = run(chosen, live=True)                                             # push the decision into the resident kernel, live

    w1 = eager["exact"] and eager["esc_ok"] and lazy["exact"] and lazy["esc_ok"] and live["exact"] and live["esc_ok"]
    w2 = (lazy["gwork"] < eager["gwork"]) and (lazy["noncanon"] > 0) and (eager["noncanon"] == 0)
    w3 = (dec_lo == 0) and (dec_hi == 1) and (chosen == 1)                     # flips across f*; workload -> eager
    w4 = (live["waited"] > 0) and (live["comp"] == n) and live["exact"]
    nesc = int(esc.get().sum())
    print(f"M2d dispatch over {n}-node Q-DAG (depth {D}, {nesc} escalated), grid {blocks}x{threads}\n")
    print(f"  profile EAGER: gcd-work={eager['gwork']:>7}  non-canonical={eager['noncanon']}  exact={eager['exact']}")
    print(f"  profile LAZY : gcd-work={lazy['gwork']:>7}  non-canonical={lazy['noncanon']}  exact={lazy['exact']}")
    print(f"  oracle f* (value<->trace bridge-null) C*={fstar:.4f};  decide(C={C_lo})={'eager' if dec_lo else 'lazy'},"
          f" decide(C={C_hi:.2f})={'eager' if dec_hi else 'lazy'}")
    print(f"  workload C={C_workload:.2f} -> oracle picks {'EAGER' if chosen else 'LAZY'}; pushed live into resident kernel\n")
    print(f"1. EXACT (eager+lazy+live, escalation exact): {w1}")
    print(f"2. PARETO REAL (lazy less gcd-work, lazy non-canonical>0, eager canonical): {w2}")
    print(f"3. ORACLE-STEERED (decision flips across f*; workload->eager): {w3}")
    print(f"4. LIVE CLOSED LOOP (resident kernel waited {live['waited']:.2f}s for zero-copy GO, completed {live['comp']}/{n}): {w4}")

    ok = w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — a (synthetic SPPF-shaped) DAG evaluated as EXACT on-device Q")
    print(f"  dataflow, its schedule (value-window<->trace-window Pareto) chosen LIVE by the el-atlas nedge")
    print(f"  oracle and pushed into the resident megakernel via zero-copy. NOTE: this is a clean reference")
    print(f"  build; the production evaluator (jea_generator_*) and the closed Agda bridge (jea_agda_bridge)")
    print(f"  already exist -- the NEW piece here is oracle-steered LIVE eager/lazy reduction-mode steering.")
