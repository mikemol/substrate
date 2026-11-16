# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-INV: the inversion-thesis WIDTH check. Thesis: the degeneracy-boundary's width at
# prime p = φ(p) = p−1, manifesting as the algebraic degree of the OFF-CIRCLE
# (non-torsion, non-kernel) part of the spectrum. The off-circle part = charpoly with
# the cyclotomic factors (torsion) and the (x-1)/x factors (trivial+kernel) DIVIDED OUT.
# Its irreducible-factor degrees should be governed by φ(p) = [Q(ζ_p):Q].
#
# CHEAP: charpoly + factor over Q (rational), NO eigenvalues. Compare p=3 (known) vs p=5 (bid).
import species_store as s
import sympy as sp
from sympy import symbols, factor_list, Poly, cyclotomic_poly, gcd, totient
import random
x = symbols('x')

def offcircle_profile(perm, nv, p, edges, eidx, C, Cpinv):
    """Factor the charpoly over Q; strip cyclotomic (torsion) & (x∓1) (trivial/kernel);
       return the degree-multiset of what REMAINS (the off-circle inverse-structure)."""
    T = s.rep(perm, edges, eidx, C, Cpinv)
    cp = Poly(T.charpoly(x).as_expr(), x)
    # divide out (x-1) and x as far as they go (trivial eigenvalue 1, kernel eigenvalue 0)
    for triv in [Poly(x-1,x), Poly(x,x)]:
        while True:
            q,r = sp.div(cp, triv, x)
            if r == Poly(0,x): cp = q
            else: break
    # divide out Phi_p (the p-th roots of unity = torsion) as far as it goes
    Phi = Poly(cyclotomic_poly(p,x), x)
    while cp.degree()>=Phi.degree():
        q,r = sp.div(cp, Phi, x)
        if r==Poly(0,x): cp=q
        else: break
    # also strip Phi_1=x-1 already done; strip Phi_2=x+1 (the -1 sign, lower torsion)
    for low in [Poly(x+1,x)]:
        while True:
            q,r = sp.div(cp, low, x)
            if r==Poly(0,x): cp=q
            else: break
    # factor the REMAINDER over Q; report irreducible-factor degrees
    if cp.degree()<=0: return []
    _, facs = factor_list(cp.as_expr(), x)
    degs=[]
    for f,mult in facs:
        degs += [Poly(f,x).degree()]*mult
    return sorted(degs)

def profile_class(nv, p, ctype, k=6, seed=1):
    edges,eidx,C,Cpinv = s.cyc_setup(nv)
    rng=random.Random(seed); seen=set(); reps=[]; tries=0
    while len(reps)<k and tries<8000:
        tries+=1
        perm=list(range(nv)); rng.shuffle(perm); perm=tuple(perm)
        if s.cyc_type(perm,nv)==ctype and perm not in seen:
            seen.add(perm); reps.append(perm)
    from collections import Counter
    profiles=Counter()
    for perm in reps:
        prof=tuple(offcircle_profile(perm,nv,p,edges,eidx,C,Cpinv))
        profiles[prof]+=1
    return profiles

print("=== P-INV: off-circle inverse-structure width vs φ(p) ===\n")
for p, nv, ct in [(3, 9, (3,3,3)), (3, 6, (3,3)), (5, 10, (5,5)), (5, 10, (5,))]:
    phi = int(totient(p))
    profs = profile_class(nv, p, ct, k=6, seed=2)
    print(f"p={p} (φ={phi})  nv={nv}  class {ct}:")
    for prof,cnt in profs.items():
        maxdeg = max(prof) if prof else 0
        print(f"    off-circle factor degrees {list(prof)}  (max {maxdeg})  ×{cnt}")
    print()
print("THESIS: max off-circle irreducible-factor degree tracks φ(p):  φ(3)=2, φ(5)=4.")
print("If p=5 shows max-degree-4 factors where p=3 showed max-degree-2, width=φ(p) CONFIRMED.")
