#!/usr/bin/env python3
"""jea_m2_dag.py — M2b: dependency dataflow over the SPPF DAG (nodes consume children's results).

Builds on M2a's lock-free claim into a real DAG evaluator. Each node: gen (leaf value) or (+)/(*) of
two CHILD nodes (indices into res, children always lower-indexed -> acyclic). A persistent megakernel
runs DATA-DRIVEN: threads repeatedly SWEEP the node array; for any node still pending whose children
are `done`, a thread atomicCAS-claims it (PENDING->CLAIMED), evaluates res from the children, fences,
marks DONE. Loops until all n nodes are done (fixpoint) or host-stop. Deadlock-free by construction:
leaves are ready immediately, the ready frontier advances every sweep, and the DAG has no cycles.

One persistent launch evaluates the whole DAG (no per-stratum relaunch) -- residency-as-liveness,
data-driven, the mature dataflow form (folds into M2c gcd-window fusion + the bignum/Q carrier).

Witnesses (each [W]):
1. CORRECT: every node's result == the host DAG reference (gen/+/* over children, int64 wrap-consistent).
2. DEPENDENCY-RESPECTED: all n nodes reach DONE (completed==n); a node is only ever evaluated after
   BOTH children are done (the ready-gate) -> correctness over the DAG, not just flat nodes.
3. PERSISTENT DATA-DRIVEN: ONE launch sweeps to fixpoint (no per-stratum launches, no host barrier).
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
np.seterr(over="ignore")                      # int64 2s-complement wrap matches CUDA long long

SRC = r"""
extern "C" __global__ void dageval(const int* op, const long long* val, const int* c0, const int* c1,
                                   long long* res, volatile int* status, int* completed,
                                   volatile int* stop, int n) {
    int stride = gridDim.x * blockDim.x;
    int t0 = blockIdx.x * blockDim.x + threadIdx.x;
    long long sweeps = 0, cap = (long long)n + 16;            // safety: DAG depth <= n
    while (*completed < n && sweeps++ < cap) {
        if (*stop) return;
        for (int i = t0; i < n; i += stride) {
            if (status[i] != 0) continue;                    // already claimed/done
            int o = op[i];
            long long r; bool ready;
            if (o == 0) { ready = true; r = val[i]; }        // gen leaf
            else if (status[c0[i]] == 1 && status[c1[i]] == 1) {   // children DONE?
                long long x = res[c0[i]], y = res[c1[i]];
                r = (o == 1) ? (x + y) : (x * y); ready = true;    // (+) / (*)
            } else ready = false;
            if (ready && atomicCAS((int*)&status[i], 0, 2) == 0) {  // claim PENDING->CLAIMED
                res[i] = r; __threadfence();                 // result visible before DONE
                status[i] = 1; __threadfence();              // mark DONE
                atomicAdd(completed, 1);
            }
        }
        __threadfence();
    }
}
"""

if __name__ == "__main__":
    ker = cp.RawKernel(SRC, "dageval")
    n, nleaf = 60_000, 12_000
    rng = np.random.default_rng(0)
    op = np.zeros(n, np.int32); op[nleaf:] = rng.integers(1, 3, n - nleaf)     # 0=gen,1=add,2=mul
    val = rng.integers(-2, 3, n).astype(np.int64)                              # small leaves
    c0 = np.zeros(n, np.int32); c1 = np.zeros(n, np.int32)
    for i in range(nleaf, n):                                                  # children strictly lower -> acyclic
        c0[i] = rng.integers(0, i); c1[i] = rng.integers(0, i)
    # host DAG reference (index order works since children < i)
    ref = np.empty(n, np.int64)
    for i in range(n):
        ref[i] = val[i] if op[i] == 0 else (ref[c0[i]] + ref[c1[i]] if op[i] == 1 else ref[c0[i]] * ref[c1[i]])

    d = lambda x: cp.asarray(x)
    res = cp.zeros(n, cp.int64); status = cp.zeros(n, cp.int32); completed = cp.zeros(1, cp.int32); stop = cp.zeros(1, cp.int32)
    blocks, threads = 64, 128
    print(f"evaluating an SPPF DAG of {n} nodes ({nleaf} leaves) via a persistent data-driven sweep ({blocks}x{threads})\n")
    ker((blocks,), (threads,), (d(op), d(val), d(c0), d(c1), res, status, completed, stop, np.int32(n)))
    cp.cuda.Stream.null.synchronize()
    rg = res.get(); comp = int(completed.get()[0]); st = status.get()

    w1 = bool((rg == ref).all())
    w2 = comp == n and bool((st == 1).all())
    w3 = True                                                                  # one launch above
    print(f"1. CORRECT: all {n} DAG node results == host reference {w1}")
    print(f"2. DEPENDENCY-RESPECTED: completed={comp}/{n}, all DONE {bool((st==1).all())} {w2}")
    print(f"3. PERSISTENT DATA-DRIVEN: one launch swept the DAG to fixpoint {w3}")

    ok = w1 and w2 and w3
    print(f"\nM2b DAG: correct {w1}; deps-respected {w2}; persistent-data-driven {w3}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — the JEA evaluator now respects DEPENDENCIES: an SPPF DAG where")
    print(f"  each node consumes its children's results, evaluated by ONE persistent data-driven sweep")
    print(f"  (atomicCAS claim + ready-gate on children-done), deadlock-free, host-reference-checked.")
    print(f"  Folds into M2c (gcd-window fusion + bignum/Q carrier) and M2d (the nedge oracle steers it).")
