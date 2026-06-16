#!/usr/bin/env python3
"""jea_sppf.py — the SPPF interning the apex eval path USES (not a demo): a ℚ-DAG -> its canonical shared SPPF.

This is the WIRED form of the trace/SPPF work. jea_carrier_solve imports `intern` and runs it BEFORE the apex
drain, so the running evaluator computes each distinct subterm ONCE (memoization = SPPF; the charter's "on-GPU
resident memoizing traces"). It is REUSED (jea_intern.intern_device = device hash-cons, cupy.unique per height);
nothing here is a standalone capability demo -- the consumer is the eval path.

intern(g): hash-cons the ℚ-DAG (op/vN/vD/lch/rch) to its canonical SPPF. Leaves keyed by (vN,vD); combines by
(op, canonical children). Returns (canonical g, distinct, collapse-info). Root value preserved (sharing merges
structurally-identical = value-identical nodes). Canonical ids are assigned bottom-up by height -> leaves-first,
so the result is a valid topological order for the apex drain.
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_intern as INT                                       # device hash-cons (cupy.unique per height) -- REUSED


def _heights(g):
    """ht[i] = 0 for leaves, max(ht children)+1 for combines (DAG is leaves-first / children-before-parents)."""
    N=g["N"]; ht=np.zeros(N, np.int64)
    for i in range(N):
        if g["op"][i]!=-1: ht[i]=max(int(ht[g["lch"][i]]), int(ht[g["rch"][i]]))+1
    return ht


def intern(g):
    """ℚ-DAG -> canonical shared SPPF (memoization). Returns (gc, distinct) where gc has the apex DAG fields."""
    N=g["N"]
    leafcodes={}; val=np.zeros(N, np.int64)                    # small injective leaf code (raw values overflow int64)
    for i in range(N):
        if g["op"][i]==-1:
            key=(int(g["vN"][i]), int(g["vD"][i]))
            val[i]=leafcodes.setdefault(key, len(leafcodes)+1)  # code>0 (combines key on op,children at height>0)
    gi=dict(val=val, lch=np.array(g["lch"],np.int64), rch=np.array(g["rch"],np.int64),
            op=np.array(g["op"],np.int64), ht=_heights(g), N=N, root=g["root"])
    canon, distinct, _v, _h = INT.intern_device(gi)            # the DEVICE-SIDE parallel dedup (reused)
    rep={}
    for orig in range(N):
        k=int(canon[orig])
        if k not in rep: rep[k]=orig
    cN=[0]*distinct; cD=[1]*distinct; cop=[-1]*distinct; clch=[-1]*distinct; crch=[-1]*distinct
    for k in range(distinct):
        o=rep[k]
        if g["op"][o]==-1: cN[k]=int(g["vN"][o]); cD[k]=int(g["vD"][o])
        else: cop[k]=int(g["op"][o]); clch[k]=int(canon[g["lch"][o]]); crch[k]=int(canon[g["rch"][o]])
    gc=dict(vN=cN, vD=cD, op=cop, lch=clch, rch=crch, N=distinct, root=int(canon[g["root"]]),
            L=sum(1 for x in cop if x==-1))                    # leaves-first, so L = leading leaf count
    if "truth" in g: gc["truth"]=g["truth"]
    return gc, distinct
