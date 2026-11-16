# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# The user's prior: a FLAT zero = a higher-order zero-divisor I'm measuring at the wrong
# order. The det-test is order-1 (T annihilates a vector). Look HIGHER on the nv=9
# (3,3,3) data where det was flatly 0/60:
#   (A) nilpotency: is (T-I)^k = 0 for some k>1? (degree>1 zero-divisor / nilpotent)
#   (B) product annihilation: N_a * N_b = 0 for distinct (3,3,3) actions? (the cross zero-div)
#   (C) the order-3 coboundary: T^3 = I clean, or T^3 - I nilpotent? (3-torsion residue)
#   (D) determinant was nonzero -- but is the spectrum ON the unit circle / roots of unity
#       (a DIFFERENT kind of degeneracy: torsion not annihilation)?
import species_store as s
import sympy as sp, random
nv=9; edges,eidx,C,Cpinv=s.cyc_setup(nv); dim=C.shape[0]; I=sp.eye(dim)
random.seed(5)
# collect distinct (3,3,3) actions
acts=[]; seen=set()
tries=0
while len(acts)<14 and tries<6000:
    tries+=1
    perm=list(range(nv)); random.shuffle(perm); perm=tuple(perm)
    if s.cyc_type(perm,nv)==(3,3,3) and perm not in seen:
        seen.add(perm)
        T=sp.simplify(s.rep(perm,edges,eidx,C,Cpinv))
        acts.append((perm,T))
print(f"collected {len(acts)} distinct (3,3,3) actions at nv=9 (dim {dim})")
Z=sp.zeros(dim,dim)
# (A) nilpotency of N=T-I, and (C) T^3-I
nilp=0; t3I=0; t3nil=0
for perm,T in acts:
    N=sp.simplify(T-I)
    Nk=N; idx=None
    for k in range(1,dim+2):
        if sp.simplify(Nk)==Z: idx=k; break
        Nk=sp.simplify(Nk*N)
    T3=sp.simplify(T*T*T-I)
    if idx and idx>1: nilp+=1
    if T3==Z: t3I+=1
    else:
        # is T^3-I nilpotent (3-torsion residue, the higher-order zero-divisor)?
        M=T3; Mk=M
        for k in range(1,dim+2):
            if sp.simplify(Mk)==Z: t3nil+=1; break
            Mk=sp.simplify(Mk*M)
print(f"  (A) (T-I) nilpotent deg>1: {nilp}/{len(acts)}")
print(f"  (C) T^3=I (clean order-3): {t3I}/{len(acts)} | T^3-I nilpotent (3-torsion residue): {t3nil}/{len(acts)}")
# (B) product annihilation N_a*N_b=0 across distinct actions
zd=0; checked=0
for i in range(len(acts)):
    Ni=sp.simplify(acts[i][1]-I)
    if Ni==Z: continue
    for j in range(len(acts)):
        if i==j: continue
        Nj=sp.simplify(acts[j][1]-I)
        if Nj==Z: continue
        checked+=1
        if sp.simplify(Ni*Nj)==Z: zd+=1
print(f"  (B) product-annihilation N_a*N_b=0 (distinct pairs): {zd}/{checked}")
# (D) spectrum: are eigenvalues roots of unity / on unit circle (torsion degeneracy)?
perm,T=acts[0]
ev={sp.nsimplify(k):v for k,v in T.eigenvals().items()}
print(f"  (D) sample spectrum: {ev}")
# how many eigenvalues have |lambda|=1 (on the unit circle = torsion)?
onunit=0; tot=0
for k,m in T.eigenvals().items():
    tot+=m
    try:
        if sp.simplify(sp.Abs(k)-1)==0: onunit+=m
    except: pass
print(f"      eigenvalues on unit circle (|λ|=1, torsion): {onunit}/{tot}")
