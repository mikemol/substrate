#!/usr/bin/env python3
"""jea_ackermann_gpu.py — the spawn loop ON-DEVICE: a non-primitive-recursive function evaluated
on the GPU, exact, batch-parallel. The universality spit-take running on silicon.

The spec (jea_ackermann_spec) showed escalation = recursion = one spawn loop. For Ackermann the
spawn structure collapses to the classic ITERATIVE STACK: a per-thread stack of m-values + a
running n. The stack IS the suspended continuation (the not-yet-unfolded recursion); each pop
unfolds one step; push = spawn, pop = resolve. NO host recursion, NO call stack — the recursion
lives in the explicit per-thread stack, in device memory.

A single Ackermann is sequential (the spawn chain has width 1), so the PARALLELISM is a BATCH of
independent evaluations: thousands of dynamic-spawn term-rewrites running at once, each exact.

ON SUSPENDED GENERATORS (user): tractable Ackermann (reachable step counts) keeps n within u64 (n
grows +1 per step; 2^64 steps is unreachable), so multi-limb is NOT exercised here — the value and
the step count are bounded together. The suspended-generator / constructive-CF-unfold-on-demand
carrier (vs GMP's eager limbs) pays off for TRACTABLE-step / HUGE-value computations (factorial,
powers): there the value's CONSTRUCTION is carried and digits unfolded on demand. That is the
escalation-spawn taken to its conclusion, and the next brick (a separate workload from Ackermann).
"""
import os, time
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
import jea_core

_SRC = r'''
extern "C" __global__
void ackermann_batch(const int* mIn, const unsigned long long* nIn,
                     unsigned long long* out, int* ovf, int* gstack, int maxstack, int B)
{
    int t = blockIdx.x*blockDim.x + threadIdx.x; if (t >= B) return;
    int* stack = gstack + (long long)t*maxstack;          // this thread's continuation stack
    int sp = 0;
    unsigned long long n = nIn[t];
    stack[sp++] = mIn[t];
    while (sp > 0) {
        int m = stack[--sp];                              // pop = resolve one step
        if (m == 0) { n = n + 1; }                        // A(0,n) = n+1  (terminal)
        else if (n == 0) {                                // A(m,0) = A(m-1,1)  (tail rewrite)
            if (sp+1 > maxstack) { ovf[t]=1; return; }
            stack[sp++] = m-1; n = 1;
        } else {                                          // A(m,n) = A(m-1, A(m,n-1))  (spawn inner)
            if (sp+2 > maxstack) { ovf[t]=1; return; }
            stack[sp++] = m-1; stack[sp++] = m; n = n - 1;
        }
    }
    out[t] = n;
}
'''
_kern = jea_core.build_kernel(_SRC, "ackermann_batch")


def ack_ref(m, n):
    while True:
        if m == 0: return n + 1
        if n == 0: m -= 1; n = 1; continue
        n = ack_ref(m, n - 1); m -= 1                      # one level of recursion, rest iterative


def max_stack_needed(m, n):
    sp = 0; mx = 0; stack = [m]
    while stack:
        mx = max(mx, len(stack)); m = stack.pop()
        if m == 0: n += 1
        elif n == 0: stack.append(m-1); n = 1
        else: stack.append(m-1); stack.append(m); n -= 1
    return mx


if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100000)
    # a pool of distinct (m,n) cases (tractable step counts, u64-safe values)
    cases = [(0,5),(1,7),(2,4),(2,6),(3,2),(3,3),(3,5),(3,6),(3,7)]
    expected = {c: ack_ref(*c) for c in cases}
    maxstack = max(max_stack_needed(*c) for c in cases) + 16
    print("Ackermann ON GPU — the spawn loop on silicon, batch-parallel, exact\n")
    print(f"  distinct cases (value = A(m,n)): " + ", ".join(f"A{c}={expected[c]}" for c in cases))
    print(f"  per-thread stack depth needed: {maxstack-16} (sized {maxstack})\n")

    B = 200000                                            # 200k independent Ackermann evaluations
    rng = np.random.default_rng(1)
    pick = rng.integers(0, len(cases), B)
    mIn = cp.asarray([cases[i][0] for i in pick], cp.int32)
    nIn = cp.asarray([cases[i][1] for i in pick], cp.uint64)
    out = cp.zeros(B, cp.uint64); ovf = cp.zeros(B, cp.int32)
    gstack = cp.zeros(B*maxstack, cp.int32)
    nblk = (B+255)//256

    def run():
        _kern((nblk,),(256,),(mIn,nIn,out,ovf,gstack,np.int32(maxstack),np.int32(B)))
        cp.cuda.Stream.null.synchronize()
    run()                                                 # warm
    t0=time.perf_counter(); run(); ms=(time.perf_counter()-t0)*1e3

    res = out.get(); exp = np.array([expected[cases[i]] for i in pick], np.uint64)
    ok = bool((res == exp).all()) and int(ovf.get().sum())==0
    print(f"  {B:,} independent Ackermann evaluations on GPU in {ms:.2f} ms "
          f"({B/ms*1e3/1e6:.1f}M evals/s), 256 threads/block")
    print(f"  every result == host reference (recursion lives in the device stack, no host calls): {ok}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — a NON-primitive-recursive function evaluated on the GPU, exact,")
    print(f"  via dynamic spawning (push/pop on the per-thread continuation stack). Universality on silicon.")
    print(f"  (Single Ackermann is sequential; parallelism = the batch. Multi-limb via suspended-generator")
    print(f"   CF-unfold-on-demand is the next brick, for tractable-step/huge-value workloads, not this one.)")
