# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import sys; sys.path.insert(0,'.')
import species_store as s, sympy as sp
from sympy import symbols,Poly,cyclotomic_poly,factor_list
import random
x=symbols('x')
def phi_mult(perm,nv,p):
    edges,eidx,C,Cpinv=s.cyc_setup(nv)
    T=s.rep(perm,edges,eidx,C,Cpinv)
    cp=Poly(T.charpoly(x).as_expr(),x);Phi=Poly(cyclotomic_poly(p,x),x);m=0
    while cp.degree()>=Phi.degree():
        q,r=sp.div(cp,Phi,x)
        if r==Poly(0,x):cp=q;m+=1
        else:break
    return m
def cyc_decomp(perm,nv):
    seen=[False]*nv;out=[]
    for st in range(nv):
        if seen[st]:continue
        c=[];x0=st
        while not seen[x0]:seen[x0]=True;c.append(x0);x0=perm[x0]
        if len(c)>1: out.append(tuple(c))
    return out
p,nv=3,9
rng=random.Random(0); reps=[]
# EXACTLY the witness's selection
while len(reps)<6:
    perm=list(range(nv));rng.shuffle(perm);perm=tuple(perm)
    if s.cyc_type(perm,nv)==(3,3,3) and perm not in reps: reps.append(perm)
print("witness-style random (3,3,3) reps: Φ_3 mult + cycle decomposition")
for perm in reps:
    m=phi_mult(perm,nv,p); dec=cyc_decomp(perm,nv)
    print(f"  Φ_3 mult={m}  cycles={dec}")
print()
# my construction: partition into sorted triples, cyclic order = increasing
def build_sorted(triples,nv):
    p=list(range(nv))
    for t in triples:
        c=sorted(t)
        for i in range(3): p[c[i]]=c[(i+1)%3]
    return tuple(p)
print("my-style (each 3-cycle = increasing cyclic order on sorted triple):")
for triples in [[(0,1,2),(3,4,5),(6,7,8)],[(0,3,6),(1,4,7),(2,5,8)],[(0,2,4),(1,3,5),(6,7,8)]]:
    perm=build_sorted(triples,nv); m=phi_mult(perm,nv,p); dec=cyc_decomp(perm,nv)
    print(f"  Φ_3 mult={m}  cycles={dec}")
