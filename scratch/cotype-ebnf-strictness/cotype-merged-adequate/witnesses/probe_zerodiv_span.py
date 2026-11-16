# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# The rung-5 die-out = 10 singular V2s, kernels don't share a vector. Question: do their
# kernels SPAN a coherent structure (sum of kernels), and what's its dim/rank? Is the
# "annihilation" a low-rank distributed object (the twisted residue)? Compare rung 3 (centralized)
# vs rung 5 (distributed): rank of the sum of all singular-V2 kernels, and the SHARED structure.
import sympy as sp
from itertools import combinations, permutations
from math import comb

def cyc_setup(nv):
    edges=list(combinations(range(nv),2)); eidx={e:i for i,e in enumerate(edges)}
    tree=set((0,j) for j in range(1,nv)); rows=[]
    for e in edges:
        if e in tree: continue
        a,b=e; v=[0]*len(edges); v[eidx[e]]+=1
        if a!=0: v[eidx[(0,a)]]-=1
        if b!=0: v[eidx[(0,b)]]+=1
        rows.append(v)
    C=sp.Matrix(rows); Cpinv=C.T*(C*C.T).inv()
    return edges,eidx,C,Cpinv
def rep(p,edges,eidx,C,Cpinv):
    m=len(edges); P=sp.zeros(m,m)
    for j,(a,b) in enumerate(edges):
        pa,pb=p[a],p[b]; e2=(pa,pb) if pa<pb else (pb,pa); P[eidx[e2],j]=1
    return C*P*Cpinv
def cyc_type(g,nv):
    seen=[False]*nv;parts=[]
    for s in range(nv):
        if seen[s]:continue
        l=0;x=s
        while not seen[x]:seen[x]=True;x=g[x];l+=1
        parts.append(l)
    return tuple(sorted([c for c in parts if c>1],reverse=True)) or (1,)

def analyze(n):
    nv=n+1; dim=comb(n,2)
    edges,eidx,C,Cpinv=cyc_setup(nv); I=sp.eye(dim)
    v2s=[p for p in permutations(range(nv)) if cyc_type(p,nv)==(2,2)]
    seen={}; acts=[]
    for g in v2s:
        T=rep(g,edges,eidx,C,Cpinv); k=tuple(T)
        if k not in seen: seen[k]=g; acts.append((g,sp.simplify(T)))
    sing=[(g,T) for g,T in acts if sp.simplify(T.det())==0]
    print(f"\nrung {n} (S{nv}, dim {dim}): {len(sing)} singular V2s")
    if not sing: return
    # collect all kernel vectors
    allker=[]
    for g,T in sing:
        for w in T.nullspace(): allker.append(w)
    K=sp.Matrix.hstack(*allker)
    span=K.rank()
    # common (intersection) = nullspace of stacked
    stacked=sp.Matrix.vstack(*[T for _,T in sing])
    common=stacked.nullspace()
    print(f"  total kernel vectors: {len(allker)} | SPAN (sum of kernels) rank: {span}/{dim} | COMMON (intersection) dim: {len(common)}")
    # the COMPLEMENT: image side. rank of sum of (T) images
    print(f"  -> annihilation occupies a {span}-dim subspace; {'CENTRALIZED' if len(common)>0 else 'DISTRIBUTED'} (common dim {len(common)})")
    # is the span itself an invariant / coherent? check if span is acted-on cleanly:
    # rank of span vs dim tells how much of cycle space the zero-divisor structure touches
    return span, len(common)

if __name__=="__main__":
    import sys
    for n in range(int(sys.argv[1]), int(sys.argv[2])+1):
        analyze(n)
