# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-COPRIME head-to-head: squarefree-coprime (2,3,5) order 30 on nv=10.
# External frame bids: PURELY cyclotomic (full divisor lattice of 30).
# Our (2,3)-data bids: non-cyclotomic cross-factor PERSISTS.
# Cheap: one charpoly, factor over Q, match against Φ_m. REPORT non-cyclotomic (never divide out).
import species_store as s
import sympy as sp
from sympy import symbols, factor_list, Poly, cyclotomic_poly, divisors
x=symbols('x')

nv=10
edges,eidx,C,Cp=s.cyc_setup(nv)
# (2,3,5): (0 1)(2 3 4)(5 6 7 8 9)
perm=[1,0, 3,4,2, 6,7,8,9,5]
perm=tuple(perm)
print(f"element (2,3,5) on nv={nv}: {perm}  cyc_type={s.cyc_type(perm,nv)}")
import math
order=1
for c in s.cyc_type(perm,nv): order=order*c//math.gcd(order,c)
print(f"order = {order}, divisors = {divisors(order)}")
print(f"dim = {C.shape[0]}")

T=s.rep(perm,edges,eidx,C,Cp)
# verify T^order ?= I (the lemma-check we now ALWAYS run before deriving roots-of-unity)
isI = sp.simplify(T**order - sp.eye(C.shape[0]))==sp.zeros(C.shape[0],C.shape[0])
print(f"T^{order} == I ? {isI}   (if False, the rep is deformed; non-cyc expected)")

cp=Poly(T.charpoly(x).as_expr(),x)
print(f"charpoly degree {cp.degree()}")
_,facs=factor_list(cp.as_expr(),x)
cyclo=[]; noncyc=[]
for f,m in facs:
    fp=Poly(f,x); d=fp.degree(); k=None
    for kk in range(1,61):
        if Poly(cyclotomic_poly(kk,x),x).monic()==fp.monic(): k=kk;break
    if k is not None: cyclo.append((k,m))
    else: noncyc.append((d,m,sp.factor(f)))
print(f"\nCYCLOTOMIC factors: {sorted(cyclo)}")
print(f"  (divisor lattice of 30 would be Φ_m for m in {divisors(30)})")
print(f"NON-CYCLOTOMIC factors: {[(f'deg{d}', f'x{m}') for d,m,_ in noncyc]}")
print()
total_noncyc_deg = sum(d*m for d,m,_ in noncyc)
print(f"VERDICT: non-cyclotomic total degree = {total_noncyc_deg}")
if total_noncyc_deg==0:
    print("  PURELY CYCLOTOMIC -> EXTERNAL FRAME WINS (squarefree-coprime is abelian)")
else:
    print(f"  NON-CYCLOTOMIC PERSISTS ({total_noncyc_deg}) -> OUR DATA WINS (cross-factor survives even squarefree-coprime)")
