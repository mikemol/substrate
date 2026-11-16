# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-DEFORM/P-TREE: does WHICH PRIME RAMIFIES follow the projection basis (the lens/focus)?
# Build the cycle-space projection from DIFFERENT spanning trees; for the SAME permutation,
# measure v_p(disc) of the non-cyclotomic factors for p=2,3,5. If the ramifying prime CHANGES
# with the tree, ramification is basis-relative (lens confirmed). Honor the warning: locate the
# actual fixed structure per basis (don't assume eigenvalue 1), and use ORIENTED fundamental cycles.
import sympy as sp
from sympy import symbols, Poly, factor_list, cyclotomic_poly
from itertools import combinations
import collections
x=symbols('x')

def edges_of(nv): return list(combinations(range(nv),2))

def C_oriented(nv, tree_edges):
    """ORIENTED fundamental-cycle basis from a spanning tree. For each non-tree edge e=(a,b),
       fundamental cycle = e minus the oriented tree path a->b. Proper signs."""
    edges=edges_of(nv); eidx={e:i for i,e in enumerate(edges)}
    tset=set(tuple(sorted(e)) for e in tree_edges)
    adj=collections.defaultdict(list)
    for a,b in tset: adj[a].append(b); adj[b].append(a)
    def oriented_path(uu,vv):
        prev={uu:None}; q=[uu]
        while q:
            n=q.pop(0)
            if n==vv: break
            for m in adj[n]:
                if m not in prev: prev[m]=n; q.append(m)
        steps=[]; cur=vv
        while cur!=uu:
            p=prev[cur]; steps.append((p,cur)); cur=p   # oriented step p->cur
        return list(reversed(steps))
    rows=[]
    for e in edges:
        es=tuple(sorted(e))
        if es in tset: continue
        a,b=e
        v=[0]*len(edges); v[eidx[es]] += 1   # +edge a->b (a<b)
        for (p_,c_) in oriented_path(a,b):
            ec=tuple(sorted((p_,c_)))
            sign = 1 if (p_<c_) else -1     # orientation of the tree edge vs its sorted form
            v[eidx[ec]] -= sign
        rows.append(v)
    return sp.Matrix(rows), edges, eidx

def rep_T(perm, nv, tree_edges):
    C,edges,eidx = C_oriented(nv, tree_edges)
    if C.rows==0: return None
    Cpinv=C.T*(C*C.T).inv()
    m=len(edges); P=sp.zeros(m,m)
    for j,(a,b) in enumerate(edges):
        pa,pb=perm[a],perm[b]; e2=(pa,pb) if pa<pb else (pb,pa); P[eidx[e2],j]=1
    return C*P*Cpinv

def vp(n,p):
    n=abs(int(n))
    if n==0: return None
    v=0
    while n%p==0: n//=p; v+=1
    return v

def ramification_profile(T):
    cp=Poly(T.charpoly(x).as_expr(),x)
    _,fl=factor_list(cp.as_expr(),x)
    prof=[]
    for f,m in fl:
        fp=Poly(f,x);k=None
        for kk in range(1,40):
            if Poly(cyclotomic_poly(kk,x),x).monic()==fp.monic():k=kk;break
        if k is None and fp.degree()>=2:
            lcm_den=1
            for c in fp.all_coeffs(): lcm_den=sp.lcm(lcm_den,sp.denom(sp.nsimplify(c)))
            Pint=Poly(sp.expand(fp.as_expr()*lcm_den),x)
            try:
                disc=Pint.discriminant()
                prof.append((fp.degree(), vp(disc,2), vp(disc,3), vp(disc,5)))
            except: prof.append((fp.degree(),"?","?","?"))
    return prof

# same permutation (4,3) order-12 on nv=7, THREE different spanning trees (three bases/foci)
nv=7
perm=[1,2,3,0,5,6,4]; perm=tuple(perm)
trees = {
  "star@0 (2-adic root)":  [(0,1),(0,2),(0,3),(0,4),(0,5),(0,6)],
  "path 0-1-..-6":         [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6)],
  "star@3 (root elsewhere)":[(3,0),(3,1),(3,2),(3,4),(3,5),(3,6)],
}
for name,tree in trees.items():
    T=rep_T(perm,nv,tree)
    if T is None: print(f"{name}: empty"); continue
    prof=ramification_profile(T)
    print(f"{name}: non-cyc factors (deg, v2disc, v3disc, v5disc):")
    for deg,v2,v3,v5 in prof:
        print(f"    deg-{deg}: v2={v2} v3={v3} v5={v5}")
    print()
print("If the RAMIFYING PRIME (which v_p>0) changes with the tree -> ramification is BASIS-RELATIVE")
print("(lens/focus confirmed). If 2 always ramifies regardless of tree -> 2 is intrinsically special.")
