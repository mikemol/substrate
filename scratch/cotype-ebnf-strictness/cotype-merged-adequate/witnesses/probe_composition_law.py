# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# COMPOSITIONAL (not tournament): is charpoly(multi-block) = compose(block charpolys)?
# Keep EVERY factor, attribute each to a block or a cross-term. No winner declared.
# A multi-block element acts block-diagonally on WITHIN-block edges and on CROSS-block edges.
# Candidate law: the factorization decomposes as
#    {within-block factors} (one block's own action)  +  {cross-block factors} (Mackey tensor).
# We VERIFY by reconstruction: compute each block ALONE (the other points fixed), get its
# factor set; then see whether charpoly(combined) = product of (block-alone factors) × (cross factors),
# and characterize the cross factors (abelian/cyclotomic on odd-coprime, non-abelian through 2).
import species_store as s
import sympy as sp
from sympy import symbols, factor_list, Poly, cyclotomic_poly, gcd, divisors
x=symbols('x')

def build(cycles, nv):
    p=list(range(nv))
    for cyc in cycles:
        for i in range(len(cyc)): p[cyc[i]]=cyc[(i+1)%len(cyc)]
    return tuple(p)

def factors(perm, nv):
    edges,eidx,C,Cp=s.cyc_setup(nv)
    T=s.rep(perm,edges,eidx,C,Cp)
    cp=Poly(T.charpoly(x).as_expr(),x)
    _,fl=factor_list(cp.as_expr(),x)
    out=[]
    for f,m in fl:
        fp=Poly(f,x); k=None
        for kk in range(1,61):
            if Poly(cyclotomic_poly(kk,x),x).monic()==fp.monic(): k=kk;break
        out.append((fp.degree(), m, ("Φ%d"%k if k else "NC"), fp))
    return out, cp

def fset(facs):  # multiset of (degree, tag) for comparison
    from collections import Counter
    return Counter((d,t) for d,m,t,_ in facs for _ in range(m))

nv=10
# the three blocks ALONE (each is the single cycle, rest fixed) on the SAME nv=10 carrier
blocks = {
  "2-block (0 1)":        build([(0,1)], nv),
  "3-block (2 3 4)":      build([(2,3,4)], nv),
  "5-block (5 6 7 8 9)":  build([(5,6,7,8,9)], nv),
}
print("=== block char-poly factor sets (each block alone, nv=10) ===")
blockf={}
for name,perm in blocks.items():
    f,_=factors(perm,nv); blockf[name]=fset(f)
    cyc=[t for d,m,t,_ in f if t!="NC" for _ in range(m)]
    nc =[(d,m) for d,m,t,_ in f if t=="NC"]
    print(f"  {name}: cyclo={sorted(cyc)}  NC={nc}")
print()

# pairwise compositions
print("=== pairwise (does the PAIR introduce a CROSS factor beyond the two blocks?) ===")
pairs = {
  "(2,3)":   build([(0,1),(2,3,4)], nv),
  "(2,5)":   build([(0,1),(5,6,7,8,9)], nv),
  "(3,5)":   build([(2,3,4),(5,6,7,8,9)], nv),
}
for name,perm in pairs.items():
    f,_=factors(perm,nv)
    cyc=[t for d,m,t,_ in f if t!="NC" for _ in range(m)]
    nc =[d*m for d,m,t,_ in f if t=="NC"]
    print(f"  {name}: cyclo={sorted(cyc)}  NC-total-deg={sum(nc)}  ({'2 involved' if '2' in name else 'ODD-ODD'})")
print()

# the full triple
print("=== triple (2,3,5) ===")
f,_=factors(build([(0,1),(2,3,4),(5,6,7,8,9)],nv),nv)
cyc=[t for d,m,t,_ in f if t!="NC" for _ in range(m)]
nc =[d*m for d,m,t,_ in f if t=="NC"]
print(f"  (2,3,5): cyclo={sorted(cyc)}  NC-total-deg={sum(nc)}")
print()
print("COMPOSITION LAW under test: cross factor is CYCLOTOMIC (Φ_{mn}) on odd-coprime pairs,")
print("NON-CYCLOTOMIC whenever the 2-block participates. Read the pair rows: (3,5) should show")
print("a clean Φ15 cross; (2,3) and (2,5) should show NON-cyclotomic cross.")
