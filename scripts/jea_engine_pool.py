#!/usr/bin/env python3
"""jea_engine_pool.py — the COMMON STRUCTURE under "fixed-DAG fold" vs "spawn/rewrite" (correcting C2's
either/or). One reduce-step `reduce(node) -> EMIT value | SPAWN children`, scheduled by readiness over a
pool that GROWS iff a rule spawns. Both the ℚ-fold and the rewrite engine are instances:

  * fixed-DAG ℚ-fold  = every rule TERMINAL (add/mul/leaf; children pre-exist) -> pool never grows.
  * rewrite (E(n))    = a SPAWN rule (E(n>0) -> spawn two E(n-1), rewrite self to add) -> pool grows.
  * escalation        = also a spawn (a wider-carrier retry node) -- the same act (not coded here, named).

This is the suspended-generator primitive (jea_core / jea_nedge_model generator_step): observe a ready
node, EMIT a value or CARRY residue. The residue is the (a,b) gcd pair at the VALUE level (combine_window
already carries it across windows) and SPAWNED CHILDREN at the STRUCTURE level -- same shape, recursively.
So spawn is NOT a distinct evaluation model: the fixed-DAG combine is the no-spawn SPECIAL CASE of one
emit-or-spawn reduce-step. (Carrier-typedef generality is C1/C3; this brick is the spawn<->fold unification.)

Witnesses (each [W]):
1. Q-FOLD via the pool engine: a random +/x DAG reduces to its Python-Fraction truth (rules all terminal,
   pool STATIC) -- same answer as the coop/strat schedulers.
2. REWRITE via the SAME engine: E(n) -> 2^n (a SPAWN rule, pool GROWS at runtime) -- same answer as
   jea_universal_engine.
3. COMMON STRUCTURE: the SAME kernel + reduce-step runs both; fixed-DAG = no-spawn (pool static),
   rewrite = spawn (pool grows). One emit-or-spawn reduce-step, two regimes.
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from fractions import Fraction
from jea_generator_dag import build_dag

ADD, MUL, LEAF, SPAWN = 0, 1, 2, 3
_SRC = r'''
typedef unsigned long long u64;
extern "C" __global__
void pool(int* op,int* narg,int* lch,int* rch, u64* vN,u64* vD, volatile int* status,
          volatile int* qtail, volatile int* pending, volatile int* err, int npool, long long maxsweep,
          int* out_sweeps)
{
    int t=blockIdx.x*blockDim.x+threadIdx.x, stride=gridDim.x*blockDim.x; long long sw=0;
    while (*pending>0 && sw++<maxsweep) {
        int qt=*qtail;
        for (int i=t;i<qt;i+=stride) {
            if (status[i]!=0) continue;
            int o=op[i];
            if (o==3) {                                  // SPAWN rule: EMIT (leaf) or SPAWN children
                if (atomicCAS((int*)&status[i],0,2)==0) {
                    int n=narg[i];
                    if (n==0) { vN[i]=1; vD[i]=1; __threadfence(); status[i]=1; atomicSub((int*)pending,1); }
                    else {
                        int c=atomicAdd((int*)qtail,2);
                        if (c+1<npool) {
                            op[c]=3;narg[c]=n-1;lch[c]=-1;rch[c]=-1;vN[c]=0;vD[c]=1;status[c]=0;
                            op[c+1]=3;narg[c+1]=n-1;lch[c+1]=-1;rch[c+1]=-1;vN[c+1]=0;vD[c+1]=1;status[c+1]=0;
                            lch[i]=c;rch[i]=c+1; op[i]=0; __threadfence();   // rewrite self to ADD (tail-rewrite)
                            atomicAdd((int*)pending,2); status[i]=0;         // children pending; self re-pends as ADD
                        } else { *err=1; vN[i]=0; vD[i]=1; status[i]=1; atomicSub((int*)pending,1); }
                    }
                }
            } else if (o==0 || o==1) {                   // ADD/MUL: TERMINAL combine (the Q reduce)
                int L=lch[i],R=rch[i];
                if (status[L]==1 && status[R]==1) {
                    if (atomicCAS((int*)&status[i],0,2)==0) {
                        u64 nl=vN[L],dl=vD[L],nr=vN[R],dr=vD[R];
                        u64 na=(o==1)?(nl*nr):(nl*dr+nr*dl), D=dl*dr;
                        u64 a=na,b=D; while(b){u64 r=a%b;a=b;b=r;} u64 g=a?a:1ULL;
                        vN[i]=na/g; vD[i]=D/g; __threadfence(); status[i]=1; atomicSub((int*)pending,1);
                    }
                }
            }
        }
        __threadfence();
    }
    if (t==0) *out_sweeps = (int)sw;
}
'''
_kern = cp.RawKernel(_SRC, "pool")


def _run(op, narg, lch, rch, vN, vD, status, pending, qtail0, npool, maxsweep):
    """maxsweep = the STRUCTURAL termination bound (critical-path depth), derived per-input by the caller --
    NOT the old 4_000_000 fuel. Termination is PROVEN by the well-founded measure (narg n strictly decreases
    each spawn, base n==0 emits -> the spawned DAG is finite); the sweep count needed to drain it is bounded by
    its dependency DEPTH (each sweep advances the frontier one level). The bound adapts to the work."""
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]; blocks, threads = 8*nsm, 128
    d = lambda a, t: cp.asarray(a, t)
    op=d(op,cp.int32); narg=d(narg,cp.int32); lch=d(lch,cp.int32); rch=d(rch,cp.int32)
    vN=d(vN,cp.uint64); vD=d(vD,cp.uint64); status=d(status,cp.int32)
    qtail=cp.full(1,qtail0,cp.int32); pend=cp.full(1,pending,cp.int32); err=cp.zeros(1,cp.int32)  # qtail0 = allocated-so-far
    sweeps=cp.zeros(1,cp.int32)
    _kern((blocks,),(threads,),(op,narg,lch,rch,vN,vD,status,qtail,pend,err,np.int32(npool),
                                np.int64(maxsweep),sweeps))
    cp.cuda.Stream.null.synchronize()
    return vN.get(), vD.get(), int(qtail.get()[0]), int(err.get()[0]), int(pend.get()[0]), int(sweeps.get()[0])


def _dag_depth(lch, rch, N):
    """critical-path depth of the fixed DAG (children indices < parent in build_dag's bottom-up order)."""
    lvl = [0]*N
    for i in range(N):
        l, r = lch[i], rch[i]
        if l >= 0 or r >= 0:
            lvl[i] = 1 + max(lvl[l] if l >= 0 else 0, lvl[r] if r >= 0 else 0)
    return max(lvl) if N else 0


def run_qfold(g):
    """fixed-DAG: rules all terminal (add/mul/leaf), pool STATIC (npool=N, no spawn)."""
    N=g["N"]
    op=[(2 if g["op"][i]==-1 else g["op"][i]) for i in range(N)]   # leaf -> LEAF, else add/mul
    narg=[0]*N; lch=list(g["lch"]); rch=list(g["rch"]); vN=list(g["vN"]); vD=list(g["vD"])
    status=[1 if op[i]==LEAF else 0 for i in range(N)]; pending=sum(1 for i in range(N) if op[i]!=LEAF)
    bound = 6*_dag_depth(lch, rch, N) + 16                         # STRUCTURAL: 6x critical-path depth (was 4M fuel)
    gn,gd,qt,err,pend,sw=_run(op,narg,lch,rch,vN,vD,status,pending,N,N,bound)  # qtail0=N (all pre-allocated), npool=N
    r=g["root"]; return Fraction(int(gn[r]),int(gd[r])), qt, N, err, pend, sw, bound


def run_rewrite(ns, cap):
    """rewrite: seed SPAWN_E roots; pool GROWS via spawn. Returns each root's value."""
    K=len(ns); op=[SPAWN]*cap; narg=[0]*cap; lch=[-1]*cap; rch=[-1]*cap
    vN=[0]*cap; vD=[1]*cap; status=[2]*cap                       # status 2 (skip) for unallocated slots
    for i,n in enumerate(ns): op[i]=SPAWN; narg[i]=n; status[i]=0
    # pending = K real seeds; qtail0=K (only seeds allocated); the pool GROWS into [K,cap) via spawn
    bound = 6*max(ns) + 16                                          # STRUCTURAL: 6x spawn-depth (narg descent), not 4M fuel
    gn,gd,qt,err,pend,sw=_run(op,narg,lch,rch,vN,vD,status,K,K,cap,bound)
    return [int(gn[i]) for i in range(K)], qt, err, pend, sw, bound


if __name__ == "__main__":
    # 1. Q-fold on the pool engine
    g=build_dag(64,3); val,qt,N,err,pend,sw1,b1=run_qfold(g)
    w1 = val==g["truth"] and err==0 and pend==0 and qt==N      # pool STATIC (qt==N, no spawn)
    # 2. rewrite E(n)=2^n on the SAME engine
    ns=[8,10,12]; cap=sum((2<<n) for n in ns)+len(ns)+16
    vals,qt2,err2,pend2,sw2,b2=run_rewrite(ns,cap)
    w2 = vals==[1<<n for n in ns] and err2==0 and pend2==0 and qt2>len(ns)   # pool GREW (spawn)
    w3 = w1 and w2                                             # SAME kernel ran both
    # Δ-J2: termination governed by a STRUCTURAL bound (critical-path depth), not the old 4M fuel.
    w4 = (sw1 <= b1) and (sw2 <= b2) and err==0 and err2==0    # actual sweeps within the DERIVED bound, correct
    print("common structure: one emit-or-spawn reduce-step runs BOTH the Q-fold and the rewrite\n")
    print(f"1. Q-FOLD via pool engine: root={val} == truth {g['truth']}; pool STATIC (qtail={qt}==N): {w1}")
    print(f"2. REWRITE via SAME engine: E{ns} -> {vals} == {[1<<n for n in ns]}; pool GREW (qtail {len(ns)}->{qt2}): {w2}")
    print(f"3. COMMON STRUCTURE (one kernel/reduce-step; fixed-DAG = no-spawn special case of emit-or-spawn): {w3}")
    print(f"4. Δ-J2 TERMINATION = STRUCTURAL BOUND, not fuel: Q-fold {sw1} sweeps <= depth-bound {b1}; "
          f"rewrite {sw2} <= spawn-depth-bound {b2} (old fuel was 4,000,000): {w4}")
    ok=w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — spawn is NOT a distinct evaluation model: the fixed-DAG combine is the")
    print(f"  NO-SPAWN special case of one reduce-step `reduce(node) -> emit | spawn`. emit-or-carry is the")
    print(f"  generator_step primitive at the VALUE level (gcd residue) AND the STRUCTURE level (spawned")
    print(f"  children) -- recursively. C2's 'spawn is a separate axis' was the either/or; this is the join.")
    print(f"  FOLD-IN: this reduce-step subsumes combine_window (terminal rules) + universal_engine (spawn)")
    print(f"  + escalation (spawn a wider carrier) -- the C-arc's real scheduler is the growable pool.")
