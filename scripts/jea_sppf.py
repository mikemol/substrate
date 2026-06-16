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
import jea_zsppf as Z                                          # SPPF = device radix-sort of z-codes (intern_radix)


def intern(g):
    """ℚ-DAG -> canonical shared SPPF (memoization). Returns (gc, distinct) where gc has the apex DAG fields.
    Interning is the DEVICE radix sort (jea_zsppf.intern_radix, the SPPF=prefix-sort-of-z-codes realization)."""
    N=g["N"]
    canon, distinct = Z.intern_radix(g, "z")                   # the DEVICE-SIDE radix sort + dedup = interning
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
