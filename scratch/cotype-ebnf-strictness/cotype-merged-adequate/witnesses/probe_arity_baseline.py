# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-ARITY: build the rep on 2-FACES (triangles, 3-subsets) instead of 1-faces (edges, 2-subsets).
# Carrier = C(n,3)-dimensional. Permutation acts on TRIPLES. Measure ramification: does 3 become
# the always-ramifying prime (3-successor available) or does 2 STAY special (triangle secretly
# 2-generated: cell-dim != successor-arity)?
# INSTRUMENTATION (the careful part): also check the 1-face (edge) rep on the SAME elements as a
# baseline, and compare WHICH prime dominates ramification frequency+magnitude in each.
import sympy as sp
from sympy import symbols, Poly, factor_list, cyclotomic_poly, primerange
from itertools import combinations
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

def kface_rep(perm, nv, k):
    """Permutation action on k-subsets (k-faces). k=2: edges. k=3: triangles.
       The PERMUTATION REPRESENTATION on k-subsets (not the cycle-space projection — we want the
       clean action first, to see which prime the k-ary successor supports)."""
    faces=list(combinations(range(nv),k)); fidx={f:i for i,f in enumerate(faces)}
    m=len(faces)
    P=sp.zeros(m,m)
    for j,f in enumerate(faces):
        pf=tuple(sorted(perm[v] for v in f))
        P[fidx[pf],j]=1
    return P, faces

def ramif(P, primes=tuple(primerange(2,30))):
    cp=Poly(P.charpoly(x).as_expr(),x)
    _,fl=factor_list(cp.as_expr(),x)
    nc=[]
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
                nc.append((fp.degree(),ram))
            except: nc.append((fp.degree(),"err"))
    return nc

# NOTE: pure permutation rep on k-subsets has eigenvalues = roots of unity (T^ord = I), so charpoly
# is CYCLOTOMIC and ramification trivial. The non-cyclotomic structure came from the CYCLE-SPACE
# PROJECTION (C·P·Cpinv). So to test arity we must project k-faces analogously. For k=2 that's the
# cycle space. For k=3 the analogue is the 2-dimensional homology / the boundary map ∂2: C3->C2.
# SIMPLEST faithful test: use the SAME projection idea — quotient by the image of the boundary.
# For a quick read, compare the pure k-face perm rep's NON-cyclotomic content (should be ZERO,
# confirming pure perm reps are cyclotomic) vs the projected one.
nv=6
perm=build([(0,1,2,3),(4,5)],nv)  # (4,2) order 4 — has 2-structure; small
for k in [2,3]:
    P,faces=kface_rep(perm,nv,k)
    # is the pure perm rep cyclotomic? (sanity: T^ord = I)
    nc=ramif(P)
    isImult = sp.simplify(P**12 - sp.eye(P.shape[0]))==sp.zeros(*P.shape)
    print(f"k={k}-faces (dim {len(faces)}): pure perm rep | non-cyc factors: {nc} | T^12=I: {isImult}")
print()
print("Pure perm reps on k-subsets are cyclotomic (roots of unity) — ramification comes from the")
print("PROJECTION. Next: project the k-face rep (quotient by boundary image) and compare which prime")
print("the projected ramification supports. This run establishes the baseline (pure = cyclotomic).")
