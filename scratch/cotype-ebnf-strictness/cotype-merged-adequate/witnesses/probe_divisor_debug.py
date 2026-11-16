# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import species_store as s
import sympy as sp
from sympy import symbols, factor_list, Poly, cyclotomic_poly, divisors
x=symbols('x')
nv=7
edges,eidx,C,Cp=s.cyc_setup(nv)
perm=(1,2,3,0,5,6,4)  # (4,3), order 12
T=s.rep(perm,edges,eidx,C,Cp)
print("dim:", T.shape, "det:", sp.cancel(T.det()))
# what IS T^12? should be I if eigenvalues are 12th roots of unity
T12 = T**12
isI = sp.simplify(T12 - sp.eye(T.shape[0]))==sp.zeros(*T.shape)
print("T^12 == I ?", isI)
# ACTUAL factorization of the charpoly over Q
cp=Poly(T.charpoly(x).as_expr(),x)
print("charpoly degree:", cp.degree())
_,facs=factor_list(cp.as_expr(),x)
print("ACTUAL irreducible factors over Q (degree, multiplicity):")
for f,m in facs:
    fp=Poly(f,x)
    # is this factor a cyclotomic? check Φ_k for k up to 60
    match=None
    for k in range(1,61):
        if Poly(cyclotomic_poly(k,x),x).monic()==fp.monic(): match=k; break
    print(f"   deg {fp.degree()} x{m}  {'= Φ_'+str(match) if match else '= NON-cyclotomic: '+str(f)}")
