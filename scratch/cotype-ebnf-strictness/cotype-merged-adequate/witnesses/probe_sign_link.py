# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# PIN THE LINK: singular V2 on cycle space  <=>  fixed-point-free involution  <=>  free -1 action.
# Show the 0-eigenvalue annihilated vector of the singular V2 IS the residue of the -1 action.
# Then PROBE the user's real conjecture: an analogous species indexed by "coprime to 3"
# (order-3 / 3-cycle analogue), i.e. coboundary structure one degree up.
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
def is_fpf(p,nv):  # fixed-point-free
    return all(p[i]!=i for i in range(nv))

# ---- PART 1: the -1 link, rung 5 (S6, even vertices, hosts the species) ----
def link(n):
    nv=n+1; dim=comb(n,2)
    edges,eidx,C,Cpinv=cyc_setup(nv); I=sp.eye(dim)
    print(f"\n=== rung {n} (S{nv}, dim {dim}): singular V2 <=> fixed-point-free? ===")
    for p in permutations(range(nv)):
        if cyc_type(p,nv)==(2,2):
            T=rep(p,edges,eidx,C,Cpinv)
            singular = sp.simplify(T.det())==0
            fpf = is_fpf(p,nv)
            # only print a couple representatives
    # tabulate: among all (2,2), correlate singular with fpf
    sing_fpf=0; sing_notfpf=0; nons_fpf=0; nons_notfpf=0
    for p in permutations(range(nv)):
        if cyc_type(p,nv)!=(2,2): continue
        T=rep(p,edges,eidx,C,Cpinv); singular=sp.simplify(T.det())==0; fpf=is_fpf(p,nv)
        if singular and fpf: sing_fpf+=1
        elif singular and not fpf: sing_notfpf+=1
        elif not singular and fpf: nons_fpf+=1
        else: nons_notfpf+=1
    print(f"  (2,2) class: singular&FPF={sing_fpf}  singular&¬FPF={sing_notfpf}  nonsing&FPF={nons_fpf}  nonsing&¬FPF={nons_notfpf}")
    # the FULL fixed-point-free involutions live only when nv is EVEN (perfect matching).
    # check: does a perfect-matching involution (nv/2 transpositions) act as -1-flavored?
    if nv%2==0:
        # build the (2,2,...,2) perfect matching involution
        pm=list(range(nv))
        for i in range(0,nv,2): pm[i],pm[i+1]=i+1,i
        pm=tuple(pm)
        T=rep(pm,edges,eidx,C,Cpinv)
        ev={sp.nsimplify(k):v for k,v in T.eigenvals().items()}
        print(f"  perfect-matching involution {pm}: eigenvalues {ev}")
        print(f"     det={sp.simplify(T.det())}, has 0-eigenvalue (annihilation): {0 in [sp.nsimplify(k) for k in T.eigenvals()]}")
    return

for n in (3,5):
    link(n)
