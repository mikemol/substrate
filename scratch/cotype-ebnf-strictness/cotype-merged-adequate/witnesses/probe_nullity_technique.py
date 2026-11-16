# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# Focused: the nullity technique reaches a dim>=70 case that symbolic factorization cannot, in seconds.
import os,sys,time; sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import species_store as s, numpy as np
from sympy import cyclotomic_poly, Poly, symbols, totient
x=symbols('x')
def build_c(c,p,nv):
    perm=list(range(nv))
    for j in range(c):
        cyc=list(range(j*p,(j+1)*p))
        for i in range(p): perm[cyc[i]]=cyc[(i+1)%p]
    return tuple(perm)
p,c=5,3; nv=15  # dim-91, the wall case
t0=time.time()
edges,eidx,C,Cp=s.cyc_setup(nv); T=s.rep(build_c(c,p,nv),nv if False else edges,eidx,C,Cp)
Tn=np.array(T.evalf(),dtype=complex)
coeffs=[complex(z) for z in Poly(cyclotomic_poly(p,x),x).all_coeffs()]
d=len(coeffs)-1; pw=[np.eye(Tn.shape[0],dtype=complex)]
for i in range(d): pw.append(pw[-1]@Tn)
M=sum(coeffs[i]*pw[d-i] for i in range(d+1))
nul=Tn.shape[0]-np.linalg.matrix_rank(M,tol=1e-6); mult=nul//int(totient(p))
dt=time.time()-t0
print(f"dim {Tn.shape[0]} (the 'wall' case p=5,c=3): Φ_p mult={mult} via nullity in {dt:.2f}s (symbolic factor: intractable)")
sys.exit(0 if (mult==9 and dt<30) else 1)
