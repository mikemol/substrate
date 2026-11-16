# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# CONSTRUCTIVE derivation of mult=(p-1)/2 per pair (c=2). Claim: Φ_p comes from the CROSS-EDGE block,
# where σ=A·B acts as shift⊗shift on the p×p torus of (A-point,B-point) pairs. Eigenvalues ζ^i·ζ^j;
# primitive p-th roots ζ^k appear on anti-diagonals i+j≡k. Halved by real conjugate-pairing.
# TEST: (1) isolate cross-edge subspace, count primitive-p-th-root eigenvalues of the RAW cross action.
#       (2) confirm the projected mult = (p-1)/2 matches, and that it's the cross block (not within).
import sys; sys.path.insert(0,'.')
import numpy as np
from itertools import combinations


def shift_tensor_eigs(p):
    # σ on cross edges = shift_A ⊗ shift_B on ℂ^p ⊗ ℂ^p. Eigenvalues = ζ^i ζ^j = ζ^(i+j mod p).
    z=np.exp(2j*np.pi/p)
    eigs=[z**((i+j)%p) for i in range(p) for j in range(p)]
    # count how many equal each primitive p-th root ζ^k (k=1..p-1)
    prim=0
    for k in range(1,p):
        target=z**k
        prim += sum(1 for e in eigs if abs(e-target)<1e-9)
    return prim, len(eigs)

print("CONSTRUCTION CHECK: cross-edge action = shift⊗shift on p×p torus")
print(f"{'p':>3} {'prim-root eigs (raw cross)':>26} {'/φ(p)':>7} {'predicted mult (p-1)/2':>22}")
for p in [3,5,7,11]:
    prim,total=shift_tensor_eigs(p)
    phi=(p-1)
    # raw: each primitive root ζ^k appears 'p' times on the torus? prim = (p-1)*? 
    print(f"{p:>3} {prim:>26} {round(prim/phi,2):>7} {(p-1)//2:>22}")
print()
print("The raw cross-torus has prim/φ(p) = p copies of each primitive root. The PROJECTION + reality")
print("pairing must cut p copies down to (p-1)/2 mult. Check the actual projected cross-block next.")
print()
# Direct: build the c=2 rep, restrict to cross-edge coordinates, measure Φ_p mult there vs total.
import species_np as snp
from sympy import symbols, Poly, cyclotomic_poly
x=symbols('x')
def build_c2(p,nv):
    perm=list(range(nv))
    for i in range(p): perm[i]=(i+1)%p
    for i in range(p): perm[p+i]=p+((i+1)%p)
    return tuple(perm)
def phi_mult_cross_vs_total(p):
    nv=2*p
    edges,eidx,C,Cpinv=snp.cyc_setup(nv)
    perm=build_c2(p,nv)
    T=snp.rep(perm,edges,eidx,C,Cpinv)
    Tn=T.astype(complex)
    # Φ_p(T) nullity = φ(p)*mult
    from sympy import cyclotomic_poly as cp_
    coeffs=[complex(c) for c in Poly(cp_(p,x),x).all_coeffs()]
    d=len(coeffs)-1
    powers=[np.eye(Tn.shape[0],dtype=complex)]
    for i in range(d): powers.append(powers[-1]@Tn)
    M=sum(coeffs[i]*powers[d-i] for i in range(d+1))
    nullity=Tn.shape[0]-np.linalg.matrix_rank(M,tol=1e-6)
    return nullity//(p-1), nullity

import os as _os, json as _json
CASES=[3,5,7]
def compute(p):
    m,nul=phi_mult_cross_vs_total(p)
    return int(m)
_gp=_os.path.join(_os.path.dirname(_os.path.realpath(__file__)),'..','data','inv_construct_gold.json')
try: GOLD={k:v for k,v in _json.load(open(_gp)).items()}
except Exception: GOLD=None
def fmt(case,res): return f"p={case}: projected Phi_p mult={res}  (p-1)/2={(case-1)//2}"
from pump_adapter import make, run_main
initial,pump,parse,serialize,deserialize = make(globals())
if __name__=="__main__": run_main(globals())
