# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-FROB: Dedekind-Kummer Frobenius inventory. For a char-poly factor f(x) in Z[x], reduce mod
# many primes p (skipping those dividing disc f); the factorization-block DEGREES = cycle type of
# Frob_p in Gal(f). Sample primes -> inventory conjugacy classes (cycle types) -> infer the Galois
# group. Confirm the deg-9 factor's Frob_3 = [5,4] (our earlier mod-3 measurement).
import species_store as s
import sympy as sp
from sympy import symbols, Poly, factor_list, cyclotomic_poly, primerange, gcd
from collections import Counter
x=symbols('x')

def build(cycles,nv):
    p=list(range(nv))
    for cyc in cycles:
        for i in range(len(cyc)): p[cyc[i]]=cyc[(i+1)%len(cyc)]
    return tuple(p)

def noncyc_factors(perm,nv):
    edges,eidx,C,Cp=s.cyc_setup(nv)
    T=s.rep(perm,edges,eidx,C,Cp)
    cp=Poly(T.charpoly(x).as_expr(),x)
    _,fl=factor_list(cp.as_expr(),x)
    out=[]
    for f,m in fl:
        fp=Poly(f,x);k=None
        for kk in range(1,40):
            if Poly(cyclotomic_poly(kk,x),x).monic()==fp.monic():k=kk;break
        if k is None: out.append(fp)
    return out

def to_int_poly(fp):
    lcm_den=1
    for c in fp.all_coeffs(): lcm_den=sp.lcm(lcm_den,sp.denom(sp.nsimplify(c)))
    return Poly(sp.expand(fp.as_expr()*lcm_den),x)

def frob_cycle_type(Pint, p):
    """Factor Pint mod p; return the multiset of factor degrees = Frob_p cycle type.
       Valid only if p does not divide disc (else ramified, skip)."""
    try:
        fl=sp.factor_list(Pint.as_expr(), x, modulus=p)
        degs=[]
        for g,m in fl[1]:
            degs += [Poly(g,x,modulus=p).degree()]*m
        return tuple(sorted(degs,reverse=True))
    except Exception:
        return None

# target: the deg-9 factor from (4,3) on nv=7
perm=build([(0,1,2,3),(4,5,6)],7)
facs=noncyc_factors(perm,7)
print(f"(4,3) nv=7: {len(facs)} non-cyclotomic factors, degrees {[f.degree() for f in facs]}")
for fp in facs:
    Pint=to_int_poly(fp)
    d=Pint.degree()
    disc=Pint.discriminant()
    print(f"\n--- factor degree {d} ---")
    # squarefree? if disc=0 the factor has repeated roots
    if disc==0:
        print("   disc=0 (not separable as integer poly) — skip Frobenius inventory")
        continue
    types=Counter()
    bad=[]
    for p in primerange(2, 60):
        if disc % p == 0: bad.append(p); continue   # ramified
        ct=frob_cycle_type(Pint,p)
        if ct and sum(ct)==d:   # full degree (unramified, valid Frobenius)
            types[ct]+=1
    print(f"   ramified primes (p|disc, skipped): {bad[:12]}")
    print(f"   Frobenius cycle-type inventory (unramified p<60):")
    for ct,cnt in types.most_common():
        print(f"      {ct}: {cnt} primes")
    # check Frob_3 specifically
    if 3 not in bad:
        f3=frob_cycle_type(Pint,3)
        print(f"   Frob_3 cycle type = {f3}   (earlier mod-3 measurement was [5,4] for the deg-9)")
    else:
        print(f"   3 is ramified (3|disc) for this factor")
