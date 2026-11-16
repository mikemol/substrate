# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import os,sys; sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
# DERIVE dim(Φ_p eigenspace) = (p-1)^2/2, step by step, checking each step computationally.
# The eigenspace lives redundantly on BB (within-B edges) and X (cross). Use the CLEANER block to count.
# Cross X = shift_A ⊗ shift_B on p×p grid. Eigenvalues ζ^i ζ^j = ζ^(i+j). For a PRIMITIVE p-th root
# ζ^k (k=1..p-1), the eigenspace = {(i,j): i+j≡k mod p}, dimension p (a full anti-diagonal). So raw
# cross Φ_p dim = (p-1)*p [φ(p) roots × p each]. That's the unconstrained count.
# The CYCLE-SPACE (boundary) constraint + the redundancy (BB≡X) cut it. Let's count what survives.
import numpy as np


def count_steps(p):
    z=np.exp(2j*np.pi/p)
    # STEP 1: raw cross-torus Φ_p dim = sum over k=1..p-1 of #{(i,j): i+j≡k} = (p-1)*p
    raw = (p-1)*p
    # STEP 2: the cross edges are UNORDERED in the actual graph? No — cross edge (a,b), a in A, b in B,
    # is one edge, and (i,j) with i=a's index, j=b's index IS ordered (A!=B). So cross is genuinely p×p.
    # STEP 3: the cycle-space constraint. The cross eigenvector for ζ^k on anti-diagonal i+j≡k must be a
    # CYCLE (in ker ∂). The boundary of a cross edge (a_i, b_j) = b_j - a_i (vertices). A combination is a
    # cycle iff vertex-sums vanish. The anti-diagonal eigenvector with phase: does it close?
    # Compute directly: build cross-edge incidence, find Φ_p eigenspace INTERSECT ker(boundary).
    nv=2*p
    # cross edges only:
    Xedges=[(a,p+b) for a in range(p) for b in range(p)]
    m=len(Xedges); xidx={e:i for i,e in enumerate(Xedges)}
    # permutation shift⊗shift on cross edges
    P=np.zeros((m,m),dtype=complex)
    for j,(a,b) in enumerate(Xedges):
        na=(a+1)%p; nb=p+((b-p+1)%p); P[xidx[(na,nb)],j]=1
    # boundary of cross edges -> vertices (2p of them)
    D=np.zeros((nv,m))
    for j,(a,b) in enumerate(Xedges): D[b,j]+=1; D[a,j]+=-1
    # Φ_p eigenspace of P
    coeffs=[1.0]*p  # Φ_p for prime p
    d=len(coeffs)-1; pw=[np.eye(m,dtype=complex)]
    for i in range(d): pw.append(pw[-1]@P)
    Phi=sum(coeffs[i]*pw[d-i] for i in range(d+1))
    # Φ_p eigenspace = ker Phi
    U,sv,Vh=np.linalg.svd(Phi); r=np.sum(sv>1e-9); Eig=Vh[r:].conj().T  # cols span Φ_p eigenspace
    raw_dim=Eig.shape[1]
    # intersect with ker D: vectors v in Eig-span with D v = 0. Solve D*Eig*c=0 for c.
    DE=D@Eig
    U2,sv2,Vh2=np.linalg.svd(DE); r2=np.sum(sv2>1e-9)
    intersect_dim=Eig.shape[1]-r2
    return raw, raw_dim, intersect_dim, (p-1)**2//2

# CASES: primes. PUMP-COMPATIBLE via pump_adapter; one p per increment (heaviest at p=11).
CASES=[3,5,7,11]

def compute(p):
    raw,rawdim,inter,target=count_steps(p)
    # the DOCUMENTED finding (a negative result): cross-alone ∩ker∂ = (p-1)(p-2), NOT (p-1)^2/2.
    return {"raw":int(raw),"cross_dim":int(rawdim),"intersect":int(inter),"target":int(target),
            "raw_ok": bool(raw==(p-1)*p), "intersect_is_pm1pm2": bool(inter==(p-1)*(p-2)),
            "intersect_ne_target": bool(inter!=target or p==3)}  # p=3 is the lone coincidence

def fmt(p,res):
    return f"{p:>3} {res['raw']:>10} {res['cross_dim']:>13} {res['intersect']:>15} {res['target']:>9}"

from pump_adapter import make
import os as _os, json as _json
_gp=_os.path.join(_os.path.dirname(_os.path.realpath(__file__)),'..','data','c2_final_gold.json')
try: GOLD={k:v for k,v in _json.load(open(_gp)).items()}
except Exception: GOLD=None
def fmt(case,res): return f"p={case}: raw={res['raw']} intersect={res['intersect']} target={res['target']}"
from pump_adapter import run_main
initial,pump,parse,serialize,deserialize = make(globals())

if __name__=="__main__": run_main(globals())
