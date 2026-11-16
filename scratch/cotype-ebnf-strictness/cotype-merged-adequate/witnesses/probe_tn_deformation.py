# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# Focused witness for "T^n != I" — the deformation signature, distinct from the Ihara-closure check.
# A single (p,c) element: confirm T raised to the permutation order is NOT the identity.
import os,sys; sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import species_store as s
import numpy as np
def build(cycles,nv):
    p=list(range(nv))
    for cyc in cycles:
        for i in range(len(cyc)): p[cyc[i]]=cyc[(i+1)%len(cyc)]
    return tuple(p)
import math
nv=7; perm=build([(0,1,2,3),(4,5,6)],nv)  # order lcm(4,3)=12
edges,eidx,C,Cp=s.cyc_setup(nv)
T=s.rep(perm,edges,eidx,C,Cp); Tn=np.array(T.evalf(),dtype=complex)
order=12
Tp=np.linalg.matrix_power(Tn,order)
is_I=np.allclose(Tp,np.eye(Tn.shape[0]),atol=1e-9)
print(f"(4,3) nv=7: T^{order} == I ? {is_I}  (deformation: should be False — NOT the permutation rep)")
sys.exit(0 if not is_I else 1)  # PASS iff genuinely deformed (T^n != I)
