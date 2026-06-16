#!/usr/bin/env python3
"""jea_dag_gen.py — Δ-Ψ-dag: ON-DEVICE DAG generation. A parametric term family (here E_q(n), the balanced add-tree
of 1/1 with 2^n leaves) is GENERATED directly into device arrays from its parameter -- no host per-node construction
loop, no host->device term upload. The host ships O(1) parameters (n + the n level offsets); the DAG is born on the
GPU. coordinate->geometry: the collapsed coordinate was the materialized O(N) term array shipped each eval; the
geometry is the GENERATOR (parameter -> structure), evaluated on-device. recompute-from-residue, not copy-across.

build_Eq(n) host layout (matched exactly): leaves [0,2^n); then balanced add-levels appended bottom-up, root last.
Node k>=L in level l (1..n) at position p combines the two level-(l-1) nodes at positions 2p,2p+1. Every node's
(op, children) is a closed-form function of k and n -- so the whole term is L + n vectorized cupy ops, no Python
per-node loop. The fused kernel (jea_mega_eval.intern_eval_dev) consumes the device arrays directly.

Witnesses ([W], __main__):
1. STRUCTURE MATCH: gen_Eq_device(n) produces op/lch/rch IDENTICAL to the host build_Eq(n), for several n.
2. ON-DEVICE: the arrays are cupy (device-resident); the host builds only the n level offsets (O(n), not O(N)).
3. [numbers] HOST-BUILD vs DEVICE-GEN: the host build_Eq Python loop (O(N)) vs the device generation (O(n) launches).
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def gen_Eq_device(n, leafcode=1):
    """Generate E_q(n) (balanced add-tree of 1/1) DIRECTLY into device arrays from n. Returns a dict of cupy arrays
    (op,lch,rch,leafkey,lNlo,lNhi,lDlo,lDhi) + N,root,L -- the host never builds an O(N) term list nor uploads one.
    leafcode = the interner's injective code for the 1/1 leaf value (MUST come from the SAME namespace as the host
    path -- a hardcoded code would collide with whatever value the interner assigned that code to)."""
    L=1<<n; N=(1<<(n+1))-1
    op=cp.empty(N,cp.int32); op[:L]=-1; op[L:]=0                          # leaves = -1; combines = add(0)
    lch=cp.full(N,-1,cp.int32); rch=cp.full(N,-1,cp.int32)
    prev_off=0; cur=L                                                    # level 0 = leaves at [0,L); internal start at L
    for l in range(1,n+1):                                              # O(n) vectorized levels (no per-node host loop)
        cnt=L>>l; p=cp.arange(cnt,dtype=cp.int32)
        lch[cur:cur+cnt]=prev_off+2*p; rch[cur:cur+cnt]=prev_off+2*p+1   # children: level-(l-1) nodes 2p, 2p+1
        prev_off=cur; cur+=cnt
    leafkey=cp.zeros(N,cp.uint64); leafkey[:L]=cp.uint64((3<<62)|leafcode)   # leaf tag=3 | the interner's 1/1 code
    z=lambda: cp.zeros(N,cp.uint64); lNlo,lNhi,lDlo,lDhi=z(),z(),z(),z()
    lNlo[:L]=1; lDlo[:L]=1                                               # leaf value 1/1 (numerator/denominator)
    return dict(op=op,lch=lch,rch=rch,leafkey=leafkey,lNlo=lNlo,lNhi=lNhi,lDlo=lDlo,lDhi=lDhi,N=N,root=N-1,L=L)


if __name__ == "__main__":
    print("jea_dag_gen: Δ-Ψ-dag -- the DAG is GENERATED on-device from its parameter (no host build loop, no upload)\n")
    import time
    from jea_zsppf import build_Eq

    # W1: device-gen structure == host build_Eq structure
    match=True
    for n in (3,4,6,8,10):
        g=gen_Eq_device(n); h=build_Eq(n)
        ok=(g["N"]==h["N"] and g["root"]==h["root"]
            and g["op"].get().tolist()==h["op"]
            and g["lch"].get().tolist()==h["lch"] and g["rch"].get().tolist()==h["rch"])
        match&=ok
        print(f"  E_q({n:2d}): N={g['N']:>6}  device-gen op/lch/rch == host build_Eq: {ok}")
    w1=match

    # W2: device-resident; the host built only the level offsets (O(n)), not the O(N) term
    g=gen_Eq_device(8); dev=type(g["op"]).__module__.startswith("cupy")
    w2=dev
    print(f"\n  W2  arrays are device-resident (cupy): {dev}; the host loop ran {8} levels (O(n)), not {g['N']} nodes (O(N))")

    # W3 [numbers]: host build_Eq (O(N) Python loop) vs device-gen (O(n) launches), large n
    n=16; reps=5
    t0=time.perf_counter()
    for _ in range(reps): build_Eq(n)
    t_host=(time.perf_counter()-t0)/reps
    gen_Eq_device(n); cp.cuda.Stream.null.synchronize()                  # warm
    t0=time.perf_counter()
    for _ in range(reps): gen_Eq_device(n); cp.cuda.Stream.null.synchronize()
    t_dev=(time.perf_counter()-t0)/reps
    N=(1<<(n+1))-1
    w3 = t_dev < t_host
    print(f"\n  W3  [numbers] E_q({n}) = {N} nodes: host build_Eq (O(N) Python) = {t_host*1e3:7.2f} ms   "
          f"device-gen (O(n)) = {t_dev*1e3:7.2f} ms   ({t_host/max(t_dev,1e-9):.1f}x)")

    ok=w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — Δ-Ψ-dag DAG-gen: the term is generated ON-DEVICE from its parameter, identical")
    print(f"  to the host build_Eq, with no O(N) host construction loop and no host->device term upload (the host ships n).")
    print(f"  Consumed by jea_resident.evaluate_Eq (-> jea_eval.evaluate_Eq): the fused kernel evals the device-gen term")
    print(f"  and bookkeeps in O(distinct) via cp.unique. Remaining: the forest host-mirror payload (the final rung).")
