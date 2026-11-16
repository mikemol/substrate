# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# The user's real conjecture: an order-3 analogue of the V2/sign species, indexed by 3
# (coboundary degree 2). Probe the (3)-cycle and (3,3) classes: their cycle-space actions,
# eigenvalues (expect cube-root / 3-torsion flavor), singular (zero-divisor) members,
# and parity-by-3 (does the species live where vertex count is / isn't divisible by 3?).
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

def probe3(n):
    nv=n+1; dim=comb(n,2)
    edges,eidx,C,Cpinv=cyc_setup(nv); I=sp.eye(dim)
    print(f"\n=== rung {n} (S{nv}, dim {dim}, nv {'÷3' if nv%3==0 else 'coprime-3' if nv%3 else ''} nv%3={nv%3}) ===")
    # study the 3-cycle class and the (3,3) class
    for target in [(3,),(3,3),(2,2)]:
        reps={}
        for p in permutations(range(nv)):
            if cyc_type(p,nv)==target:
                T=rep(p,edges,eidx,C,Cpinv); k=tuple(T)
                if k not in reps: reps[k]=(p,sp.simplify(T))
        if not reps: 
            print(f"  class {target}: none at this rung"); continue
        nsing=0; samp=None
        for k,(p,T) in reps.items():
            if sp.simplify(T.det())==0: nsing+=1; 
            if samp is None: samp=(p,T)
        p,T=samp
        ev={sp.nsimplify(k):v for k,v in T.eigenvals().items()}
        # check T^3=I for 3-cycles (order-3 action)
        order3 = sp.simplify(T*T*T-I)==sp.zeros(dim,dim) if target in [(3,),(3,3)] else None
        print(f"  class {target}: {len(reps)} distinct actions, {nsing} singular | sample {p}")
        print(f"     eigenvalues: {ev}")
        if order3 is not None: print(f"     T^3=I (clean order-3 action): {order3}")
    return

if __name__=="__main__":
    import sys
    for n in range(int(sys.argv[1]), int(sys.argv[2])+1):
        probe3(n)
