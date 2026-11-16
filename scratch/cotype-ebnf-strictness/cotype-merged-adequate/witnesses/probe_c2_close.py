# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-INV-COND-c2-CLOSE: derive p -> (p-1)/2. Decompose the Φ_p-eigenspace across edge blocks and
# trace exactly what the cycle-space projection removes. Raw cross-torus: mult p per primitive root.
# Projected: (p-1)/2. Removal = (p+1)/2. WHERE does it go?
import sys; sys.path.insert(0,'.')
import numpy as np
from itertools import combinations
from sympy import totient

def analyze(p):
    nv=2*p
    A=list(range(p)); B=list(range(p,2*p))
    edges=list(combinations(range(nv),2)); eidx={e:i for i,e in enumerate(edges)}
    # block membership
    def block(e):
        a,b=e
        if a<p and b<p: return 'AA'
        if a>=p and b>=p: return 'BB'
        return 'X'
    perm=list(range(nv))
    for i in range(p): perm[i]=(i+1)%p
    for i in range(p): perm[p+i]=p+((i+1)%p)
    perm=tuple(perm)
    # FULL edge permutation matrix (unsigned), and its Φ_p-eigenspace, block by block
    m=len(edges); P=np.zeros((m,m))
    for j,(a,b) in enumerate(edges):
        pa,pb=perm[a],perm[b]; e2=(pa,pb) if pa<pb else (pb,pa); P[eidx[e2],j]=1
    z=np.exp(2j*np.pi/p)
    # for each primitive root, nullity of (P - ζ^k I) restricted by block — but eigenvectors mix blocks.
    # Instead: Φ_p multiplicity in the FULL edge perm P, and in the cycle space (ker ∂1).
    def phi_null(M):
        from sympy import Poly, cyclotomic_poly, symbols
        x=symbols('x'); coeffs=[complex(c) for c in Poly(cyclotomic_poly(p,x),x).all_coeffs()]
        d=len(coeffs)-1; pw=[np.eye(M.shape[0],dtype=complex)]
        for i in range(d): pw.append(pw[-1]@M)
        Mp=sum(coeffs[i]*pw[d-i] for i in range(d+1))
        return M.shape[0]-np.linalg.matrix_rank(Mp,tol=1e-6)
    full_null=phi_null(P)
    # boundary ∂1: edges -> vertices
    D=np.zeros((nv,m))
    for j,(a,b) in enumerate(edges): D[a,j]+=1; D[b,j]+=-1
    # cycle space = ker D ; projector onto it
    # restrict P to ker D (P preserves ker D? unsigned P may not — that's the deformation). Project:
    U,sv,Vh=np.linalg.svd(D); rank=np.sum(sv>1e-9); K=Vh[rank:].conj().T  # ker basis
    Tcyc = np.linalg.pinv(K)@P@K
    cyc_null=phi_null(Tcyc)
    phi=int(totient(p))
    print(f"p={p}: FULL edge-perm Φ_p nullity={full_null} (mult {full_null//phi}) | "
          f"cycle-space Φ_p nullity={cyc_null} (mult {cyc_null//phi}) | (p-1)/2={(p-1)//2}")
    # where do within-blocks contribute? AA block alone is A acting on C(p,2) edges of K_p:
    AAedges=[e for e in edges if block(e)=='AA']
    print(f"    edge blocks: AA={sum(1 for e in edges if block(e)=='AA')}, "
          f"BB={sum(1 for e in edges if block(e)=='BB')}, X(cross)={sum(1 for e in edges if block(e)=='X')}")
    return full_null//phi, cyc_null//phi

print("Trace p -> (p-1)/2 through the projection (full edge-perm mult vs cycle-space mult):\n")
for p in [3,5,7]:
    analyze(p)
print()
print("KEY: compare FULL edge-perm Φ_p mult (before projection) to cycle-space mult ((p-1)/2).")
print("The difference = what ∂1-projection (killing the boundary/coboundary modes) removes.")
