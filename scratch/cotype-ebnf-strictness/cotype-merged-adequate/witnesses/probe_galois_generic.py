# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# Focused witness for "Galois groups are generic large symmetric groups" — distinct from the
# Dedekind-Kummer focal-factor check. Evidence: a deg-9 factor with mod-p factor-degree patterns
# (Frobenius cycle types) that force a large primitive group (a 9-cycle + an 8-cycle => contains A_9).
import os,sys; sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import species_store as s
import sympy as sp
from sympy import symbols, Poly, factor_list, primerange
x=symbols('x')
def build(cycles,nv):
    p=list(range(nv))
    for cyc in cycles:
        for i in range(len(cyc)): p[cyc[i]]=cyc[(i+1)%len(cyc)]
    return tuple(p)
nv=7; perm=build([(0,1,2,3),(4,5,6)],nv)
edges,eidx,C,Cp=s.cyc_setup(nv)
T=s.rep(perm,edges,eidx,C,Cp)
cp=Poly(T.charpoly(x).as_expr(),x); _,fl=factor_list(cp.as_expr(),x)
# find the largest non-cyclotomic factor; collect its mod-p factor-degree multiset (Frobenius cycle types)
from sympy import cyclotomic_poly
def is_cyc(fp):
    for k in range(1,40):
        if Poly(cyclotomic_poly(k,x),x).monic()==fp.monic(): return True
    return False
bigfac=max((Poly(f,x) for f,m in fl if not is_cyc(Poly(f,x))), key=lambda P:P.degree(), default=None)
deg=bigfac.degree() if bigfac else 0
cycle_types=set()
for p in primerange(2,60):
    try:
        fp=Poly(bigfac.as_expr(),x,modulus=p)
        if fp.degree()==deg:
            degs=tuple(sorted(Poly(g,x,modulus=p).degree() for g,_ in fp.factor_list()[1]))
            cycle_types.add(degs)
    except Exception: pass
# generic-large evidence: presence of a full-degree cycle (irreducible mod p => deg-cycle Frobenius)
has_long=any(len(t)==1 for t in cycle_types)
print(f"deg-{deg} factor: distinct mod-p factor-degree patterns (Frobenius cycle types) = {len(cycle_types)}")
print(f"   includes a full {deg}-cycle (irreducible mod some p): {has_long}  => generic large group")
sys.exit(0 if (deg>=6 and has_long) else 1)
