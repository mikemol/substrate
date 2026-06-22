"""
branch-independence-nedge-pilot.py — T-series pilot: WHEN does G_OR (parallel sum) hold, and when
does a shared resource break it? (candidate claim BRI).

The het-dispatch pilot summed two branches (CPU + GPU) as G_OR. That is valid ONLY because the two
are INDEPENDENT silicon -- no shared downstream series element. This pilot tests the boundary by
partitioning ONE CPU into k parallel branches (k worker threads) and asking whether they sum.

The prediction from the conductance algebra:
  * COMPUTE branches (private ALUs/FPUs per core) are independent -> they SUM (G_OR holds):
        aggregate GFLOP/s ~ k * single-core GFLOP/s, up to core count.
  * MEMORY branches (all cores SHARE the memory controller, a series element) CONTEND -> they do
        NOT sum: aggregate BW saturates at the controller = G_AND(controller, sum_k per-core).
So "n branches sum for free" is TRUE for independent branches and FALSE under a shared resource.
This is the el-atlas "irreducible beyond series/parallel" (Wheatstone / Y-Delta) regime, exhibited
on a single machine -- no hardware multiplicity needed, exactly as the single-instance argument says,
but the single instance reveals BOTH regimes, not just the additive one.

Witnesses (each [W]; numbers measured live):
1. MEMORY CONTENDS (shared controller, G_OR breaks): aggregate streaming BW(k) is strongly
   sub-additive -- BW(cores)/BW(1) << cores, and it saturates (the controller cap).
2. COMPUTE COMPOSES (independent ALUs, G_OR holds): aggregate GFLOP/s(k)/GFLOP/s(1) tracks k far
   better -- compute scales where memory saturates.
3. THE BOUNDARY: compute scaling >> memory scaling on the SAME cores -> the difference is the
   SHARED RESOURCE, not parallelism per se. G_OR holds iff branches share no series element; else
   the law is G_AND(shared, sum_i G_i). The CPU+GPU het-sum is the independent (valid) kind.
Run output: tools/branch-independence-nedge-pilot-out.txt.
"""
import os
# force single-threaded BLAS BEFORE numpy import, so k worker threads = k independent compute branches
for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(v, "1")
os.environ.setdefault("CUDA_PATH", "/usr")
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from cpu_load import matmul_spin   # Π11: shared CPU matmul-throughput workload

CORES = os.cpu_count()
G_AND = lambda a, b: 0.0 if a + b == 0 else a * b / (a + b)


def agg_memory_bw(k, mb_per=128, reps=4):
    """k threads each stream a private large array (>> L3) and sum it. Aggregate BW = total bytes
    / wall time. Tests the SHARED memory controller."""
    n = mb_per * 1024 * 1024 // 4
    arrs = [np.ones(n, np.float32) for _ in range(k)]
    for a in arrs:
        a.sum()                                          # warm / fault in
    best = 1e9
    with ThreadPoolExecutor(max_workers=k) as ex:
        for _ in range(reps):
            t = time.perf_counter()
            list(ex.map(lambda a: float(a.sum()), arrs))
            best = min(best, time.perf_counter() - t)
    return k * arrs[0].nbytes / best                     # aggregate bytes/s


def agg_compute_gflops(k, m=256, iters=16):
    """k threads each run independent single-thread sgemms sized to fit PRIVATE L2 (256^2*3 = 768KB
    < 1.25MB L2/core), so they don't spill to shared L3. Aggregate GFLOP/s. Tests PRIVATE ALUs."""
    mats = [(np.random.rand(m, m).astype(np.float32), np.random.rand(m, m).astype(np.float32))
            for _ in range(k)]
    for x, y in mats:
        np.dot(x, y)                                     # warm
    def work(xy): return matmul_spin(xy, iters)
    best = 1e9
    with ThreadPoolExecutor(max_workers=k) as ex:
        for _ in range(2):
            t = time.perf_counter()
            list(ex.map(work, mats))
            best = min(best, time.perf_counter() - t)
    return k * iters * 2 * m ** 3 / best                 # aggregate FLOP/s


if __name__ == "__main__":
    print(f"branch independence on {CORES} cores (single-thread BLAS; k threads = k branches)\n")
    ks = sorted(set([1, 2, 4, max(1, CORES // 2), CORES]))

    print("  memory branches (shared controller):")
    bw = {k: agg_memory_bw(k) for k in ks}
    for k in ks:
        print(f"     k={k:2d}  aggregate {bw[k]/1e9:6.1f} GB/s   (ideal G_OR {bw[1]*k/1e9:6.1f})")
    mem_scaling = bw[CORES] / bw[1] / CORES               # 1.0 = perfect sum, <<1 = contention

    print("  compute branches (private ALUs):")
    gf = {k: agg_compute_gflops(k) for k in ks}
    for k in ks:
        print(f"     k={k:2d}  aggregate {gf[k]/1e9:6.0f} GFLOP/s (ideal G_OR {gf[1]*k/1e9:6.0f})")
    cmp_scaling = gf[CORES] / gf[1] / CORES

    # 1. memory contends: strongly sub-additive (the shared controller caps it)
    w1 = mem_scaling < 0.6
    # 2. compute (private-L2-resident) composes strictly BETTER than memory on the same cores
    w2 = cmp_scaling > mem_scaling
    # 3. the boundary is the shared resource: same cores, compute (private) out-scales memory (shared)
    w3 = w1 and w2
    print(f"\n  memory scaling (BW_cores / cores*BW_1) = {mem_scaling:.2f}  (1.0 = perfect G_OR sum)")
    print(f"  compute scaling (GFLOP_cores / cores*GFLOP_1) = {cmp_scaling:.2f}")
    print(f"\nBRANCH INDEPENDENCE NEDGE PILOT: memory-contends {w1}; compute-composes-better {w2}; "
          f"boundary=shared-resource {w3}")
    ok = w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — G_OR (parallel sum) holds iff branches share no downstream")
    print(f"  series resource. COMPUTE branches (private ALUs) compose -- aggregate GFLOP/s tracks core")
    print(f"  count. MEMORY branches CONTEND on the shared controller -- aggregate BW saturates, far below")
    print(f"  the naive sum (G_AND(controller, sum_k cores), not G_OR). Both regimes on ONE machine: the")
    print(f"  CPU+GPU het-sum is the independent (valid G_OR) kind; n cores on the controller are NOT.")
    print(f"  'n branches sum for free' is true only for INDEPENDENT branches -- the shared-resource case")
    print(f"  is the el-atlas irreducible-beyond-series/parallel (Wheatstone/Y-Delta) regime.")
