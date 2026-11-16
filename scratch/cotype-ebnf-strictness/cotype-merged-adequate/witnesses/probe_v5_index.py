# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-V5: INDEX the residue v5=3 (5 ramifies in deg-6 factor of (4,3)@nv=7, no 5-cycle).
# Climb-checks: which family does it live in?
#   F_n:   vary the CARRIER nv (4,3) embedded in nv=7,8,9,10 — does v5 persist/climb?
#   F_ord: vary the ELEMENT to other order-12 (e.g. (4,3) vs a 12-cycle) — order-family?
#   control: is 5 special, or do OTHER primes ramify too (maybe everything ramifies, 5 not special)?
import sympy as sp
from sympy import symbols, Poly, factor_list, cyclotomic_poly, primerange
x=symbols('x')

def build(cycles,nv):
    p=list(range(nv))
    for cyc in cycles:
        for i in range(len(cyc)): p[cyc[i]]=cyc[(i+1)%len(cyc)]
    return tuple(p)

def vp(n,p):
    n=abs(int(n))
    if n==0: return None
    v=0
    while n%p==0: n//=p; v+=1
    return v

def ramif_profile(perm,nv,primes=(2,3,5,7,11,13)):
    edges,eidx,C,Cp=__import__('species_store').cyc_setup(nv)
    import species_store as s
    T=s.rep(perm,edges,eidx,C,Cp)
    cp=Poly(T.charpoly(x).as_expr(),x)
    _,fl=factor_list(cp.as_expr(),x)
    out=[]
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
                ram={p:vp(disc,p) for p in primes if vp(disc,p)}
                out.append((fp.degree(), ram))
            except: out.append((fp.degree(),"err"))
    return out

import species_store as s
print("=== F_n climb: (4,3) embedded in growing carriers ===")
# (4,3) needs 7 points; embed in nv=7,8,9,10 (extra points fixed)
for nv in [7,8,9,10]:
    perm=build([(0,1,2,3),(4,5,6)],nv)
    prof=ramif_profile(perm,nv)
    print(f"  nv={nv}: " + " | ".join(f"deg{d}:{ram}" for d,ram in prof))
print()
print("=== F_ord climb: other order-12 elements at nv=7 ===")
for name,cyc in [("(4,3)",[(0,1,2,3),(4,5,6)]),("(3,4) relabel",[(0,1,2),(3,4,5,6)])]:
    perm=build(cyc,7); prof=ramif_profile(perm,7)
    print(f"  {name}: " + " | ".join(f"deg{d}:{ram}" for d,ram in prof))
print()
print("=== control: is 5 special, or do many primes ramify (5 not special)? ===")
perm=build([(0,1,2,3),(4,5,6)],7); prof=ramif_profile(perm,7,primes=tuple(primerange(2,30)))
print(f"  (4,3)@nv=7 full ramification: " + " | ".join(f"deg{d}:{ram}" for d,ram in prof))
print()
print("INDEX: if v5 persists/climbs with nv -> F_n family. If only at nv=7 -> rung-coincidence.")
print("If many primes ramify -> 5 not special (the residue dissolves). If only 2,5 -> structured.")
