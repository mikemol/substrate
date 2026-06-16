#!/usr/bin/env python3
"""jea_sppf_apex.py — Δ-Σ-trace rung-1: the apex evaluates an INTERNED SPPF (memoizing trace), not a tree.

The SPPF orphan audit (Δ-Σ-trace) found the whole trace/SPPF cluster imported by NOBODY -- the apex evaluated
hand-built DAG ARRAYS and never used the term-algebra's trace/interning. This composes the biggest orphan:
jea_intern (device-side parallel hash-cons, U7 -- "interned-DAG = memoization = SPPF") into the apex eval path.

The eval TRACE is an SPPF: structurally-identical subterms are ONE shared node, computed ONCE (memoization).
A ℚ-term tree (every occurrence its own node) is INTERNED on-device (cupy.unique per height, REUSING
jea_intern.intern_device with an encoded ℚ-leaf key) to its canonical SPPF, which the apex (jea_apex_deliver.
run_apex_u128) drains -- each distinct subterm evaluated once. Same exact rational, far fewer combines.

This is the charter criterion realized: "on-GPU resident MEMOIZING traces" = the SPPF. recompute-from-residue,
not recompute-per-occurrence. (Δ-Σ-trace continues: hold the gcd/EEA reduction residue + the supervisor decision
WAL in the SAME SPPF structure -- one never-discard-residue trace; see the WAL ledger.)

Witnesses (each [W]):
1. INTERNED ON-DEVICE: jea_intern.intern_device dedups the ℚ tree to its canonical SPPF (cupy.unique per height);
   distinct << tree node count (the sharing the SPPF buys), reported as a collapse ratio.
2. APEX EVALUATES THE SPPF, EXACT: run_apex_u128 on the canonical SPPF == the true rational == the apex on the
   full tree -- semantics preserved; each distinct subterm computed ONCE (memoization), far fewer combines.
3. COMPOSED, NOT ORPHANED: jea_intern is now IMPORTED by the apex eval path (import edge); the SPPF is the eval
   trace, not a hand-built array routed around the term-algebra's interning.
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_intern as INT                                   # U7 device hash-cons -- the orphan we are composing
from jea_apex_deliver import run_apex_u128


def build_Eq_tree(n):
    """A ℚ add-tree: 2^n leaves all = 1/1, balanced add up to root = 2^n / 1. Every occurrence its OWN node (a
    tree, no sharing) -- exactly what an un-interned trace looks like. Returns the apex ℚ-DAG + ht (for interning)."""
    L = 1 << n
    vN=[1]*L; vD=[1]*L; op=[-1]*L; lch=[-1]*L; rch=[-1]*L; ht=[0]*L
    level=list(range(L))
    while len(level) > 1:
        nxt=[]
        for i in range(0, len(level), 2):
            k=len(vN); vN.append(0); vD.append(1); op.append(0); lch.append(level[i]); rch.append(level[i+1])
            ht.append(ht[level[i]]+1); nxt.append(k)
        level=nxt
    return dict(vN=vN, vD=vD, op=op, lch=lch, rch=rch, N=len(vN), root=level[0], ht=np.array(ht, np.int64)), n


def intern_q(g):
    """Intern the ℚ-DAG to its canonical SPPF, REUSING jea_intern.intern_device (device hash-cons). Encode each
    ℚ leaf (vN,vD) as a single key so structurally-equal leaves dedup; combines key on (op, canonical children).
    Returns the canonical ℚ-SPPF dict (op/vN/vD/lch/rch/N/root) -- leaves-first (intern assigns ids by height)."""
    N=g["N"]; BIG=1<<40
    val=np.array([ (g["vN"][i]*BIG + g["vD"][i]) if g["op"][i]==-1 else 0 for i in range(N) ], np.int64)  # ℚ-leaf key
    gi=dict(val=val, lch=np.array(g["lch"],np.int64), rch=np.array(g["rch"],np.int64),
            op=np.array(g["op"],np.int64), ht=g["ht"], N=N, root=g["root"])
    canon, distinct, _value, hgpu = INT.intern_device(gi)        # <-- the DEVICE-SIDE parallel dedup (reused)
    rep={}                                                       # one representative orig per canonical id
    for orig in range(N):
        k=int(canon[orig])
        if k not in rep: rep[k]=orig
    cN=[0]*distinct; cD=[1]*distinct; cop=[-1]*distinct; clch=[-1]*distinct; crch=[-1]*distinct
    for k in range(distinct):
        o=rep[k]
        if g["op"][o]==-1: cN[k]=g["vN"][o]; cD[k]=g["vD"][o]
        else: cop[k]=g["op"][o]; clch[k]=int(canon[g["lch"][o]]); crch[k]=int(canon[g["rch"][o]])
    return dict(vN=cN, vD=cD, op=cop, lch=clch, rch=crch, N=distinct, root=int(canon[g["root"]])), distinct, hgpu


if __name__ == "__main__":
    print("Δ-Σ-trace rung-1: the apex evaluates an INTERNED SPPF (memoizing trace) -- composing jea_intern\n")
    allok=True; rows=[]
    for n in (8, 12, 14):
        tree,_=build_Eq_tree(n); truth=Fraction(1<<n,1)
        sppf, distinct, hgpu = intern_q(tree)
        tree_val,te = run_apex_u128(tree)                       # apex on the full TREE (every occurrence a node)
        sppf_val,se = run_apex_u128(sppf)                       # apex on the canonical SPPF (each subterm ONCE)
        ncomb_tree=sum(1 for i in range(tree["N"]) if tree["op"][i]!=-1)
        ncomb_sppf=sum(1 for i in range(sppf["N"]) if sppf["op"][i]!=-1)
        ok=(tree_val==truth) and (sppf_val==truth) and (distinct==n+1)   # E(n) canonical minimum = n+1
        allok &= ok
        rows.append((n,tree["N"],distinct,ncomb_tree,ncomb_sppf,sppf_val,truth,ok,hgpu))
        print(f"  E_q({n}): tree {tree['N']:>6} nodes ({ncomb_tree} combines) -> SPPF {distinct:>3} nodes ({ncomb_sppf} combines)"
              f"  {tree['N']//distinct:>5}x collapse | apex(SPPF)={sppf_val} ==truth({truth}):{sppf_val==truth} [{hgpu} GPU dedups]")

    w1 = all(r[2] < r[1] for r in rows)                         # interned: distinct << tree nodes (sharing found)
    w2 = all(r[5]==r[6] and r[7] for r in rows)                 # apex on SPPF == truth (== tree), exact + minimal
    w3 = all(r[4] < r[3] for r in rows)                         # SPPF combines << tree combines (memoization: once-per-subterm)
    print(f"\nW1 INTERNED ON-DEVICE (jea_intern.intern_device, cupy.unique per height): tree -> canonical SPPF, "
          f"distinct << nodes: {w1}")
    print(f"W2 APEX EVALUATES THE SPPF, EXACT (run_apex_u128 on the canonical SPPF == truth == apex-on-tree): {w2}")
    print(f"W3 MEMOIZATION (SPPF combines << tree combines -- each distinct subterm computed ONCE, not per-occurrence): {w3}")
    ok=w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — Δ-Σ-trace rung-1: the apex's eval trace is now an INTERNED SPPF. A ℚ tree is")
    print(f"  hash-consed ON-DEVICE (jea_intern, REUSED -- no longer orphaned) to its canonical SPPF; the apex drains")
    print(f"  the SPPF, computing each distinct subterm ONCE (memoization) to the exact rational. 'on-GPU resident")
    print(f"  MEMOIZING traces = SPPF' (charter) realized. NEXT (Δ-Σ-trace cont.): hold the gcd/EEA reduction residue")
    print(f"  (jea_carrier_trace/trace_window) + the supervisor decision WAL in the SAME SPPF -- one trace; intern the")
    print(f"  REAL workloads (build_dag / the Agda SPPF jea_agda_dag) before the apex, not just the E_q demonstrator.")
