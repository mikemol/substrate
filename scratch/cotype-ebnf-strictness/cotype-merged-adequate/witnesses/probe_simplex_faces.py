# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# USER: every tower level installs the level below as FACES of a higher-order simplex.
# So a block doesn't act on n linear slots — it acts on the FACE LATTICE (edges = 1-faces).
# PREDICTION: the "deformation" (non-cyclotomic) degrees = the ORBIT LENGTHS of the permutation
# acting on the simplicial faces (edges), NOT vertex-periodic. T^n ≠ I because face-orbits have
# lengths that are NOT divisors of n (they're lcm/combinatorial, non-linear in n).
import species_store as s
import sympy as sp
from sympy import symbols, factor_list, Poly, cyclotomic_poly
from itertools import combinations
x=symbols('x')

def edge_orbits(perm, nv):
    """Orbits of the permutation acting on the EDGES (1-faces of the simplex on nv vertices)."""
    edges=list(combinations(range(nv),2))
    def act(e): 
        a,b=perm[e[0]],perm[e[1]]; return (a,b) if a<b else (b,a)
    seen=set(); orbits=[]
    for e in edges:
        if e in seen: continue
        orb=[]; cur=e
        while cur not in seen:
            seen.add(cur); orb.append(cur); cur=act(cur)
        orbits.append(len(orb))
    return sorted(orbits, reverse=True)

def cp_factor_degs(perm,nv):
    edges,eidx,C,Cp=s.cyc_setup(nv)
    T=s.rep(perm,edges,eidx,C,Cp)
    cp=Poly(T.charpoly(x).as_expr(),x)
    _,fl=factor_list(cp.as_expr(),x)
    cyclo=[]; nc=[]
    for f,m in fl:
        fp=Poly(f,x);k=None
        for kk in range(1,61):
            if Poly(cyclotomic_poly(kk,x),x).monic()==fp.monic():k=kk;break
        for _ in range(m):
            (cyclo if k else nc).append((fp.degree(), "Φ%d"%k if k else "NC"))
    return cyclo, nc

def build(cycles,nv):
    p=list(range(nv))
    for c in cycles:
        for i in range(len(c)): p[c[i]]=c[(i+1)%len(c)]
    return tuple(p)

import os as _os, json as _json, math as _math
from collections import Counter as _Counter
NV=10
BLOCKS={"5-block":[(5,6,7,8,9)],"3-block":[(2,3,4)],"2-block":[(0,1)],"(2,3,5)":[(0,1),(2,3,4),(5,6,7,8,9)]}
CASES=list(BLOCKS.keys())
def compute(name):
    cycles=BLOCKS[name]; perm=build(cycles,NV)
    eo=edge_orbits(perm,NV)
    op_order=1
    for L in eo: op_order=op_order*L//_math.gcd(op_order,L)
    cyclo,nc=cp_factor_degs(perm,NV)
    return {"lcm_edge_orbits": op_order, "nc_degs": sorted([d for d,_ in nc], reverse=True)}
_gp=_os.path.join(_os.path.dirname(_os.path.realpath(__file__)),'..','data','simplex_faces_gold.json')
try: GOLD={k:v for k,v in _json.load(open(_gp)).items()}
except Exception: GOLD=None
def fmt(case,res): return f"{case}: lcm(edge-orbits)={res['lcm_edge_orbits']} nc_degs={res['nc_degs']}"
from pump_adapter import make, run_main
initial,pump,parse,serialize,deserialize = make(globals())
if __name__=="__main__": run_main(globals())
