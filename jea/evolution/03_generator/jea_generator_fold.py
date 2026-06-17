#!/usr/bin/env python3
"""jea_generator_fold.py — increment (3): the WORKER's gcd-window step_fn, closing the full
evaluator loop on-device. Same persistent primitive + handshake + exact-ℚ controller as
jea_generator_kernel.py; the worker's step_fn is now a REAL windowed ℚ reduction:

  * each worker owns ℚ nodes (N,D); a WINDOW does K Euclidean gcd steps on each PENDING node.
  * a node that converges (b==0) EMITS its reduced value (N/g, D/g) and frees its slot;
  * one that doesn't CARRIES its (a,b) residue RESIDENT across windows (charter #2 — the
    suspended generator continued, not recomputed);
  * the worker PUBLISHES the measured depth (steps a node has taken; pending ⇒ steps+1, so a
    node still going after K steps signals depth>K) as telemetry the controller steers K off.

The closed loop: K is seeded BELOW the deepest node, so the controller DISCOVERS the deep
work from telemetry and grows K to converge it in fewer windows — the fold's behavior steers
K, K steers the fold. Verified: every emitted reduction is bit-exact vs Python's gcd, every
node converges, and K climbs in response to the measured depth. (Carrier = u64 here to keep
the new MECHANISM in focus; the proven 128-bit _QDECL machinery drops in unchanged — the
windowed-refill loop is carrier-agnostic.)
"""
# --- jea-evolution rung bootstrap: jea/ foundation + sibling rungs on the path (see 00_SYLLABUS.md) ---
import os as _os, sys as _sys, glob as _glob
_EVO = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))   # .../jea/evolution
_sys.path[:0] = [_os.path.dirname(_EVO), *sorted(_glob.glob(_os.path.join(_EVO, "*", "")))]
# --- end bootstrap ---
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from math import gcd
import jea_core                                  # strict shared structure (control law, ASCII gate, residency)

_SRC = jea_core.CTRL_CUDA + r'''
extern "C" __global__
void generator_fold(
    volatile int* K, volatile int* tick, volatile int* acked, volatile int* telem,
    const unsigned long long* Na, const unsigned long long* Da,   // original node (N,D)
    unsigned long long* a, unsigned long long* b,                 // RESIDENT Euclidean residue
    int* steps, int* doneN,                                       // step counter, converged flag
    unsigned long long* outN, unsigned long long* outD,           // emitted reduced value
    int* worker_logK, volatile int* err,
    int num_workers, int nodes_per, int T, long long maxspin)
{
    if (threadIdx.x != 0) return;
    int blk = blockIdx.x;

    if (blk == 0) {
        // CONTROLLER: observe measured depth -> exact-rational relaxation -> publish K
        int Kcur = *K;                                         // host-seeded K0
        for (int t=1; t<=T; t++){
            int mx=0; for(int w=0;w<num_workers;w++){int v=telem[w]; mx=v>mx?v:mx;}
            if (t>1) Kcur = relax_q(Kcur, mx);
            *K = Kcur;  __threadfence();
            *acked=0;   __threadfence();
            *tick=t;    __threadfence();
            long long sp=0; while(*acked<num_workers){ if(++sp>maxspin){*err=1;return;} }
        }
        *tick=T+1; __threadfence();
    } else {
        // WORKER: one gcd-WINDOW per tick over its resident nodes; emit converged, carry residue
        int w=blk-1, last=0; long long sp=0; int base=w*nodes_per;
        while(true){
            int t=*tick; if(t>T) break;
            if(t>=1 && t!=last){
                int Kw = *K;                                  // OBSERVE the current window size
                int md=0;
                for(int n=0;n<nodes_per;n++){
                    int i=base+n;
                    if(!doneN[i]){
                        unsigned long long aa=a[i], bb=b[i]; int st=steps[i];
                        for(int j=0;j<Kw;j++){ if(bb!=0){ unsigned long long r=aa%bb; aa=bb; bb=r; st++; } }
                        a[i]=aa; b[i]=bb; steps[i]=st;         // CARRY residue resident
                        if(bb==0){ unsigned long long g = aa?aa:1ULL;   // EMIT reduced value
                                   outN[i]=Na[i]/g; outD[i]=Da[i]/g; doneN[i]=1; }
                    }
                    int est = doneN[i] ? steps[i] : steps[i]+1;   // pending => >K triggers a K raise
                    md = est>md? est: md;
                }
                worker_logK[w*T + (t-1)] = Kw;
                telem[w] = md;  __threadfence();              // PUBLISH measured depth
                atomicAdd((int*)acked, 1);
                last=t; sp=0;
            } else if(++sp>maxspin){ *err=2; break; }
        }
    }
}
'''
_kern = jea_core.build_kernel(_SRC, "generator_fold")
residency = jea_core.residency                  # the measured liveness invariant, shared


def run(nodes, T=40, K0=4, maxspin=200_000_000):
    """nodes = list of (N,D); replicated to every worker. Returns per-node (outN,outD),
    convergence flags, the K-trajectory each worker saw, and err."""
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]
    nblocks = min(20, nsm); num_workers = nblocks - 1
    # measured residency invariant — refuse to launch a comm graph that can't stay live.
    per_sm, max_resident, _nsm, regs = residency(_kern, 32)
    assert nblocks <= max_resident, (
        f"RESIDENCY VIOLATION: launching {nblocks} blocks but only {max_resident} can be "
        f"co-resident ({regs} regs ⇒ {per_sm}/SM × {nsm} SMs) — cyclic comm graph would deadlock.")
    run._residency = (regs, per_sm, max_resident, nblocks)
    nodes_per = len(nodes)
    total = num_workers * nodes_per
    Na = cp.asarray([N for _ in range(num_workers) for (N, _D) in nodes], cp.uint64)
    Da = cp.asarray([D for _ in range(num_workers) for (_N, D) in nodes], cp.uint64)
    a  = Na.copy(); b = Da.copy()
    steps = cp.zeros(total, cp.int32); doneN = cp.zeros(total, cp.int32)
    outN  = cp.zeros(total, cp.uint64); outD = cp.zeros(total, cp.uint64)
    K = cp.full(1, K0, cp.int32); tick = cp.zeros(1, cp.int32); acked = cp.zeros(1, cp.int32)
    telem = cp.zeros(num_workers, cp.int32)
    logK = cp.full(num_workers * T, -1, cp.int32); err = cp.zeros(1, cp.int32)
    _kern((nblocks,), (32,),
          (K, tick, acked, telem, Na, Da, a, b, steps, doneN, outN, outD, logK, err,
           np.int32(num_workers), np.int32(nodes_per), np.int32(T), np.int64(maxspin)))
    cp.cuda.Stream.null.synchronize()
    return (num_workers, nodes_per, T, outN.get(), outD.get(), doneN.get(),
            steps.get(), logK.get().reshape(num_workers, T), int(err.get()[0]))


if __name__ == "__main__":
    # node set: shallow + a DEEP Fibonacci pair (F20,F19)=(6765,4181), gcd 1, ~18 Euclid steps.
    nodes = [(6, 4), (100, 60), (6765, 4181), (8, 6)]
    nw, npr, T, outN, outD, doneN, steps, logK, err = run(nodes, T=40, K0=4)

    # 1) EXACTNESS: every emitted reduction == Python gcd reduction, bit-for-bit.
    exact = True
    for w in range(nw):
        for n, (N, D) in enumerate(nodes):
            i = w * npr + n; g = gcd(N, D)
            if (int(outN[i]), int(outD[i])) != (N // g, D // g): exact = False
    # 2) CONVERGENCE: all nodes done.
    converged = bool(doneN.all())
    # 3) CLOSED LOOP: K climbed in response to the measured deep-node depth.
    Ktraj = list(map(int, logK[0]))
    climbed = max(Ktraj) > Ktraj[0]
    deep_depth = max(int(steps[i]) for i in range(npr))   # worker-0 node depths
    depths = [int(steps[n]) for n in range(npr)]

    regs, per_sm, max_resident, launched = run._residency
    print(f"increment (3): {nw} workers + 1 controller, {npr} nodes/worker, T={T}, {cp.cuda.Device().attributes['MultiProcessorCount']} SMs\n")
    print(f"  RESIDENCY INVARIANT (measured): {regs} regs/thread => {per_sm} blocks/SM => "
          f"{max_resident} resident >= {launched} launched : {'OK' if launched <= max_resident else 'VIOLATED'}\n")
    print(f"  nodes (N,D)        : {nodes}")
    print(f"  reduced (worker 0) : {[(int(outN[n]), int(outD[n])) for n in range(npr)]}")
    print(f"  measured depths    : {depths}   (deep Fibonacci node = {deep_depth} Euclid steps)")
    print(f"  K trajectory       : {Ktraj}")
    print(f"\n  err={err}  exact-vs-Python-gcd={exact}  all-converged={converged}  K-climbed={climbed}")
    ok = (err == 0 and exact and converged and climbed)
    print(f"\n  INCREMENT (3) {'PASS' if ok else 'FAIL'} — full evaluator loop on-device: workers fold")
    print(f"  real ℚ nodes in K-windows (emit converged, carry residue resident), controller grows")
    print(f"  K off the MEASURED depth to converge the deep node faster. Reductions bit-exact.")
