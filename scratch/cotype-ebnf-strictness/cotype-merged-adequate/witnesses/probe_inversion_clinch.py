# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# Clinch: is the recurring degree-φ(p) off-circle factor LITERALLY the cyclotomic
# polynomial Φ_p (or a cyclotomic Φ_m with φ(m)=p−1)? If yes: the inverse-structure
# IS the cyclotomic field / unit group, not just degree-coincidence.
import species_store as s
import sympy as sp
from sympy import symbols, factor_list, Poly, cyclotomic_poly, totient, divisors
import random
x=symbols('x')

def offcircle_factors(perm,nv,p,edges,eidx,C,Cpinv):
    T=s.rep(perm,edges,eidx,C,Cpinv)
    cp=Poly(T.charpoly(x).as_expr(),x)
    for triv in [Poly(x-1,x),Poly(x,x),Poly(x+1,x)]:
        while True:
            q,r=sp.div(cp,triv,x)
            if r==Poly(0,x): cp=q
            else: break
    if cp.degree()<=0: return []
    _,facs=factor_list(cp.as_expr(),x)
    return [Poly(f,x) for f,m in facs for _ in range(m)]

# which cyclotomic polys have degree φ = p-1?  (Φ_m with φ(m)=p-1)
def cyclo_of_degree(d, maxm=60):
    out={}
    for m in range(1,maxm):
        if int(totient(m))==d:
            out[m]=Poly(cyclotomic_poly(m,x),x)
    return out

for p,nv,ct in [(3,9,(3,3,3)),(5,10,(5,5))]:
    phi=int(totient(p))
    edges,eidx,C,Cpinv=s.cyc_setup(nv)
    cyclos=cyclo_of_degree(phi)
    print(f"p={p} φ={phi}: cyclotomic polys of degree {phi}: Φ_m for m∈{sorted(cyclos)}")
    rng=random.Random(3); reps=[]; seen=set(); tries=0
    while len(reps)<4 and tries<8000:
        tries+=1; perm=list(range(nv)); rng.shuffle(perm); perm=tuple(perm)
        if s.cyc_type(perm,nv)==ct and perm not in seen: seen.add(perm); reps.append(perm)
    for perm in reps:
        facs=offcircle_factors(perm,nv,p,edges,eidx,C,Cpinv)
        degphi=[f for f in facs if f.degree()==phi]
        matches=[]
        for f in degphi:
            fm=f.monic()
            hit=[m for m,cyc in cyclos.items() if cyc.monic()==fm]
            matches.append(hit[0] if hit else "non-cyclotomic")
        print(f"    {len(degphi)} factors of degree {phi}: cyclotomic-match = {matches}")
    print()
print("If the degree-φ(p) factors ARE Φ_m (φ(m)=p−1): inverse-structure = cyclotomic field. CLINCHED.")
