# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-THREE, right instrument: the 3-ADIC structure of each non-cyclotomic factor.
# Cube-root-of-unity splitting (prev probe) was wrong: these factors' roots aren't roots of unity.
# 3-content in a non-cyclotomic factor = 3-adic ramification: does 3 divide the discriminant?
# how does the factor reduce mod 3? SIMPLEST 3-thing = 3 inert / unramified. DRESSED = 3 ramifies
# (3 | disc), and HOW it ramifies (simple vs higher) = 3-as-prime vs interference.
import species_store as s
import sympy as sp
from sympy import symbols, factor_list, Poly, cyclotomic_poly, discriminant, GF, factor_list as fl_mod
x=symbols('x')

def build(cycles,nv):
    p=list(range(nv))
    for c in cycles:
        for i in range(len(c)): p[c[i]]=c[(i+1)%len(c)]
    return tuple(p)

def noncyc_factors(perm,nv):
    edges,eidx,C,Cp=s.cyc_setup(nv)
    T=s.rep(perm,edges,eidx,C,Cp)
    cp=Poly(T.charpoly(x).as_expr(),x)
    _,fl=factor_list(cp.as_expr(),x)
    out=[]
    for f,m in fl:
        fp=Poly(f,x);k=None
        for kk in range(1,61):
            if Poly(cyclotomic_poly(kk,x),x).monic()==fp.monic():k=kk;break
        if k is None: out.append((fp.degree(), f))
    return out

def v3(n):  # 3-adic valuation of an integer
    n=abs(int(n)); v=0
    if n==0: return None
    while n%3==0: n//=3; v+=1
    return v

def three_profile(deg, f):
    # clear denominators to integer poly
    P=Poly(f,x)
    lcm_den=1
    for c in P.all_coeffs():
        c=sp.nsimplify(c)
        lcm_den=sp.lcm(lcm_den, sp.denom(c))
    Pint=Poly(sp.expand(f*lcm_den), x)
    # discriminant and its 3-valuation
    try:
        disc=Pint.discriminant()
        d3=v3(disc) if disc!=0 else None
    except Exception as e:
        d3="err"
    # reduction mod 3: factor over GF(3)
    try:
        modfac=sp.factor_list(Pint.as_expr(), x, modulus=3)
        moddegs=sorted([Poly(g,x).degree() for g,m in modfac[1] for _ in range(m)],reverse=True)
    except Exception as e:
        moddegs=["err"]
    return d3, moddegs

nv=10
candidates=[("lone 3-block",[(2,3,4)]),("lone 5-block",[(5,6,7,8,9)]),
            ("(2,3,5)",[(0,1),(2,3,4),(5,6,7,8,9)]),("lone 2-block",[(0,1)])]
print("P-THREE 3-adic: v3(disc) = how much 3 RAMIFIES; mod-3 factorization = how it reduces.")
print("SIMPLEST 3-thing: v3(disc)=0 (3 unramified, inert-ish). DRESSED: v3(disc)>0, and the")
print("PATTERN of v3 across factors is the signal (clean vs interference).\n")
for name,cycles in candidates:
    perm=build(cycles,nv); ncs=noncyc_factors(perm,nv)
    print(f"{name}:")
    for deg,f in ncs:
        d3,moddegs=three_profile(deg,f)
        deg3 = "3∤deg" if deg%3 else f"3|deg (deg={deg}={'3·'+str(deg//3) if deg%3==0 else deg})"
        print(f"    deg-{deg} [{deg3}]: v3(disc)={d3}  mod-3 factors-> {moddegs}")
    print()
