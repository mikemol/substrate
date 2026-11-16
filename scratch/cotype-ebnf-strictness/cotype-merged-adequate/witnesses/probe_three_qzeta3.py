# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-THREE as GAP-MEASUREMENT (not pattern-hunt). User's criterion: something always happens
# at prime p; the question is whether it's the SIMPLEST p-thing (⟹ p-as-prime, independent
# coordinate) or DRESSED (⟹ interference; the excess is itself a residue to recurse on).
#
# For each candidate non-cyclotomic factor:
#   1. predict the SIMPLEST p-structure of that degree (bare cyclotomic ramification object)
#   2. measure the observed factor against it -> the GAP
#   3. gap=0 ⟹ p-as-prime;  gap≠0 ⟹ interference, the gap is the residue.
# Exclude misattributable degrees (deg-4 = φ(5) is a 5-thing, NOT a 3-thing).
#
# Concrete instrument: factor each candidate over Q(ζ3) (a degree-2 ext that "knows about 3").
# SIMPLEST 3-thing of degree d = splits into d/φ(3-ish) pieces matching the bare 3-ramification.
# We read: does the factor SPLIT over Q(ζ3) (3-structured) or stay INERT (no 3-content)?
# And crucially: is the splitting the MINIMAL one (clean halving) or dressed (irregular)?
import species_store as s
import sympy as sp
from sympy import symbols, factor_list, Poly, cyclotomic_poly, sqrt, factor, minimal_polynomial
from itertools import combinations
x=symbols('x')
zeta3 = sp.Rational(-1,2) + sp.sqrt(3)*sp.I/2   # primitive cube root

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
        if k is None: out.append((fp.degree(), sp.factor(f), f))
    return out

def split_over_Qzeta3(poly_expr):
    """Factor poly over Q(ζ3) = Q(sqrt(-3)). Return list of factor degrees over the extension."""
    # factor over the field extension Q(sqrt(-3))
    try:
        fl = sp.factor_list(poly_expr, x, extension=sp.sqrt(-3))
        degs=[]
        for f,m in fl[1]:
            degs += [Poly(f,x).degree()]*m
        return sorted(degs, reverse=True)
    except Exception as e:
        return ["err:"+str(e)[:40]]

nv=10
candidates = [
    ("lone 3-block",      [(2,3,4)]),
    ("lone 5-block",      [(5,6,7,8,9)]),
    ("(2,3,5)",           [(0,1),(2,3,4),(5,6,7,8,9)]),
    ("lone 2-block",      [(0,1)]),
]
print("P-THREE gap-measurement: factor each NON-cyclotomic factor over Q(ζ3)=Q(√−3).")
print("SPLITS over Q(ζ3) ⟹ has 3-content; INERT ⟹ no 3-content. Minimal split ⟹ 3-as-prime;")
print("dressed/irregular split ⟹ interference (the excess is the residue).\n")
for name,cycles in candidates:
    perm=build(cycles,nv)
    ncs=noncyc_factors(perm,nv)
    print(f"{name}: {len(ncs)} non-cyclotomic factor(s)")
    for deg, fac, f in ncs:
        over3 = split_over_Qzeta3(sp.expand(f))
        rational_deg = deg
        splits = (over3 != [rational_deg] and not (len(over3)==1 and over3[0]==rational_deg))
        # is the split MINIMAL (clean halving into equal pieces) or dressed?
        verdict=""
        if not splits or over3==[rational_deg]:
            verdict="INERT over Q(ζ3) -> NO 3-content"
        else:
            from collections import Counter
            c=Counter(over3)
            if len(set(over3))==1:
                verdict=f"SPLITS into {len(over3)} equal deg-{over3[0]} -> MINIMAL 3-split (3-as-prime candidate)"
            else:
                verdict=f"SPLITS irregularly {over3} -> DRESSED (interference; excess=residue)"
        print(f"    deg-{deg} non-cyc: over Q(ζ3) -> {over3}   {verdict}")
    print()
