# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-INV-COND-c2-CLOSE (take 2): decompose the CANONICAL species_store rep (tree-frame C·P·Cpinv).
# Trace the Φ_p-eigenspace: which fundamental-cycle coordinates carry it. The star tree roots at 0.
# Non-tree edges = all edges NOT incident to 0. So fundamental cycles ~ indexed by edges (a,b) with
# a,b != 0. The cross-torus (A-point,B-point) edges with neither =0 are the carriers. Trace p->(p-1)/2.
import os,sys; sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import species_np as snp
import numpy as np
from itertools import combinations

def build_c2(p,nv):
    perm=list(range(nv))
    for i in range(p): perm[i]=(i+1)%p
    for i in range(p): perm[p+i]=p+((i+1)%p)
    return tuple(perm)

def phi_eigenspace_dim(M,p):
    coeffs=[1.0]*p  # Φ_p for prime p
    d=len(coeffs)-1; pw=[np.eye(M.shape[0],dtype=complex)]
    for i in range(d): pw.append(pw[-1]@M)
    Mp=sum(coeffs[i]*pw[d-i] for i in range(d+1))
    return M.shape[0]-np.linalg.matrix_rank(Mp,tol=1e-6)

# CASES: primes. PUMP-COMPATIBLE via pump_adapter; one p per increment. The finding: mult=(p-1)/2,
# AA block carries 0% (root deletes its block), eigenspace on BB+X.
from itertools import combinations
from collections import Counter
CASES=[3,5,7]

def compute(p):
    nv=2*p
    edges,eidx,C,Cpinv=snp.cyc_setup(nv)
    Tn=snp.rep(build_c2(p,nv),edges,eidx,C,Cpinv).astype(complex)
    phi=p-1; nul=phi_eigenspace_dim(Tn,p)
    w,V=np.linalg.eig(Tn); z=np.exp(2j*np.pi/p)
    prim_idx=[i for i,lam in enumerate(w) if any(abs(lam-z**k)<1e-6 for k in range(1,p))]
    nontree=[e for e in edges if 0 not in e]
    def blk(e):
        a,b=e
        return 'AA' if (a<p and b<p) else ('BB' if (a>=p and b>=p) else 'X')
    byblk={'AA':0.0,'BB':0.0,'X':0.0}
    if prim_idx:
        supp=np.abs(V[:,prim_idx]).sum(axis=1)
        for r,e in enumerate(nontree):
            if r<len(supp): byblk[blk(e)]+=supp[r]
    tot=sum(byblk.values()) or 1
    pct={k:round(v/tot,4) for k,v in byblk.items()}
    return {"nullity":int(nul),"mult":int(nul//phi),"target":(p-1)//2,
            "AA_share":pct['AA'],"mult_ok":bool(nul//phi==(p-1)//2),"AA_zero":bool(pct['AA']<0.01)}

def fmt(p,res):
    return (f"p={p}: nullity={res['nullity']} mult={res['mult']} (p-1)/2={res['target']} | "
            f"AA share {res['AA_share']:.1%} (root deletes its block)")

from pump_adapter import make
import os as _os, json as _json
_gp=_os.path.join(_os.path.dirname(_os.path.realpath(__file__)),'..','data','c2_close2_gold.json')
try: GOLD={k:v for k,v in _json.load(open(_gp)).items()}
except Exception: GOLD=None
def fmt(case,res): return f"p={case}: mult={res['mult']} target={res['target']} AA_zero={res['AA_zero']}"
from pump_adapter import run_main
initial,pump,parse,serialize,deserialize = make(globals())

if __name__=="__main__": run_main(globals())
