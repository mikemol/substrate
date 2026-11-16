# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-ARITY (correct, finally): literal k-generalization of the WORKING edge code. Key insight from
# reading species_store.rep: P is the UNSIGNED permutation (P[...]=1, no sign), and C is the
# spanning-TREE fundamental-cycle frame. The firing comes from unsigned-P (not a chain map) projected
# through the tree frame. My signed/kernel versions killed it. So mirror the edge code exactly at k=2.
#
# Edge code: edges=2-subsets; tree=star{(0,j)}; fundamental cycle of non-tree edge (a,b) = e - (0,a) + (0,b).
# k=2 analogue: triangles=3-subsets; "2-tree"=star-like {(0,i,j)}; fundamental 2-cycle of non-tree
#   triangle (a,b,c) = it minus the star-fillings (0,b,c)-(0,a,c)+(0,a,b). Unsigned permutation on triangles.
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
    n=abs(int(n)); 
    if n==0: return None
    v=0
    while n%p==0: n//=p; v+=1
    return v

def setup_k(nv,k):
    """k-generalization of cyc_setup: k-faces, star-spanning-k-tree (faces containing vertex 0),
       fundamental k-cycles = non-tree k-face minus its star-boundary-fillings. C, Cpinv."""
    faces=list(combinations(range(nv),k)); fidx={f:i for i,f in enumerate(faces)}
    tree=set(f for f in faces if 0 in f)   # star: all k-faces containing vertex 0
    rows=[]
    for f in faces:
        if f in tree: continue
        v=[0]*len(faces); v[fidx[f]] += 1
        # boundary of f = sum_i (-1)^i (f without i-th vertex). Replace each (k-1)-boundary-face by
        # the star-filling: the k-face {0} ∪ (that (k-1)-face), with matching sign — mirrors edge case
        # where (a,b)->(0,a),(0,b). For k=2: f=(a,b,c); fill via (0,b,c),(0,a,c),(0,a,b).
        for i in range(k):
            sub=f[:i]+f[i+1:]            # (k-1)-face
            fill=tuple(sorted((0,)+sub)) # the star k-face {0}∪sub
            if 0 in sub:                 # already contains 0; skip (it's its own boundary in star)
                continue
            if fill in fidx and fill in tree:
                v[fidx[fill]] += (-1)**i
        rows.append(v)
    C=sp.Matrix(rows)
    if C.rows==0: return None,None,None,None
    Cpinv=C.T*(C*C.T).inv()
    return faces,fidx,C,Cpinv

def rep_k(perm,faces,fidx,C,Cpinv,nv,k):
    m=len(faces); P=sp.zeros(m,m)
    for j,f in enumerate(faces):
        pf=tuple(sorted(perm[v] for v in f))
        P[fidx[pf],j]=1     # UNSIGNED, like the working edge rep
    return C*P*Cpinv

def ramif(T,primes=tuple(primerange(2,30))):
    cp=Poly(T.charpoly(x).as_expr(),x); _,fl=factor_list(cp.as_expr(),x)
    cyc=[];nc=[]
    for f,m in fl:
        fp=Poly(f,x);kk=None
        for c in range(1,40):
            if Poly(cyclotomic_poly(c,x),x).monic()==fp.monic():kk=c;break
        if kk: cyc+=[kk]*m
        elif fp.degree()>=2:
            ld=1
            for cc in fp.all_coeffs(): ld=sp.lcm(ld,sp.denom(sp.nsimplify(cc)))
            Pint=Poly(sp.expand(fp.as_expr()*ld),x)
            try: disc=Pint.discriminant(); nc.append((fp.degree(),{p:vp(disc,p) for p in primes if vp(disc,p)}))
            except: nc.append((fp.degree(),"err"))
    return sorted(cyc),nc

import os as _os, json as _json
NV=6; PERM=build([(0,1,2,3),(4,5)],NV)
CASES=[2,3]
def compute(k):
    faces,fidx,C,Cpinv=setup_k(NV,k)
    if faces is None: return {"fires": False, "nc_degs": []}
    T=rep_k(PERM,faces,fidx,C,Cpinv,NV,k)
    isI = sp.simplify(T**12 - sp.eye(T.shape[0]))==sp.zeros(*T.shape)
    cyc,nc=ramif(T)
    return {"fires": (not bool(isI)), "nc_degs": sorted([d for d,_ in nc], reverse=True)}
_gp=_os.path.join(_os.path.dirname(_os.path.realpath(__file__)),'..','data','arity_kface_gold.json')
try: GOLD={k:v for k,v in _json.load(open(_gp)).items()}
except Exception: GOLD=None
def fmt(case,res): return f"k={case}: fires={res['fires']} nc_degs={res['nc_degs']}"
from pump_adapter import make, run_main
initial,pump,parse,serialize,deserialize = make(globals())
if __name__=="__main__": run_main(globals())
