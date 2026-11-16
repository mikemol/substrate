# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# Read the factorization as a LATTICE OF INTERACTIONS, no Φ_m assumption, no dividing-out.
# Mixed elements: each is disjoint cycles on separate blocks. Internal edges -> single-prime
# (cyclotomic) factors; CROSS edges -> interaction factors (possibly non-cyclotomic).
# Test: (a) does the prime-POWER block (4=2²) generate extra non-cyclotomic structure vs
# squarefree (2)? (b) does COPRIMALITY of block sizes govern the cross structure?
import species_store as s
import sympy as sp
from sympy import symbols, factor_list, Poly, cyclotomic_poly
x=symbols('x')

def build(cycles, nv):
    """cycles = list of tuples (the explicit cycles on 0..nv-1)."""
    p=list(range(nv))
    for cyc in cycles:
        for i in range(len(cyc)):
            p[cyc[i]]=cyc[(i+1)%len(cyc)]
    return tuple(p)

def factor_profile(perm, nv):
    edges,eidx,C,Cp=s.cyc_setup(nv)
    T=s.rep(perm,edges,eidx,C,Cp)
    cp=Poly(T.charpoly(x).as_expr(),x)
    _,facs=factor_list(cp.as_expr(),x)
    out=[]
    for f,m in facs:
        fp=Poly(f,x); d=fp.degree()
        cyc=None
        for k in range(1,61):
            if Poly(cyclotomic_poly(k,x),x).monic()==fp.monic(): cyc=k;break
        out.append((d,m,("Φ%d"%cyc if cyc else "NONcyc")))
    order = 1
    import math
    for cyc in cycles_of(perm,nv):
        order = order*len(cyc)//math.gcd(order,len(cyc))
    return out, order

def cycles_of(perm,nv):
    seen=[False]*nv; out=[]
    for s0 in range(nv):
        if seen[s0]:continue
        cyc=[]; x0=s0
        while not seen[x0]: seen[x0]=True; cyc.append(x0); x0=perm[x0]
        if len(cyc)>1: out.append(cyc)
    return out

cases = [
    ("(2,3) sqfree coprime",      [(0,1),(2,3,4)],            5),
    ("(4,3) primepow×coprime",    [(0,1,2,3),(4,5,6)],        7),
    ("(4,2) primepow share-2",    [(0,1,2,3),(4,5)],          6),
    ("(2,2,3) two 2s + 3",        [(0,1),(2,3),(4,5,6)],      7),
    ("(3,3) two 3s (control)",    [(0,1,2),(3,4,5)],          6),
]
for name, cycles, nv in cases:
    perm=build(cycles,nv)
    prof, order = factor_profile(perm, nv)
    cyclo = [(d,m,t) for d,m,t in prof if t!="NONcyc"]
    noncyc= [(d,m,t) for d,m,t in prof if t=="NONcyc"]
    print(f"{name}: nv={nv} order={order} cyc_type={tuple(sorted((len(c) for c in cycles),reverse=True))}")
    print(f"   cyclotomic factors: {[(t,'x%d'%m if m>1 else '') for d,m,t in cyclo]}")
    print(f"   NON-cyclotomic:     {[('deg%d'%d,'x%d'%m if m>1 else '') for d,m,t in noncyc]}")
    print()
