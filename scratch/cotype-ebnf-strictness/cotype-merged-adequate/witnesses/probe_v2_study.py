# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# Study how V2's (double-transpositions, the (2,2) class) actually manifest in the
# cycle-space rep across S3, S4, S5 -- the user says it's non-obvious. Look at:
#   (1) which involution classes EXIST at each rung,
#   (2) for EACH involution, its cycle-space action T_g: eigenvalues, T^2=I?, fixes generic v?
#   (3) crucially: do the V2's COMMUTE in their cycle-space action, or is the weave twisted?
import sympy as sp
from itertools import combinations, permutations, product
from math import comb
from fractions import Fraction

def cyc_setup(nv):
    edges=list(combinations(range(nv),2)); eidx={e:i for i,e in enumerate(edges)}
    tree=set((0,j) for j in range(1,nv)); rows=[]
    for e in edges:
        if e in tree: continue
        a,b=e; v=[0]*len(edges); v[eidx[e]]+=1
        if a!=0: v[eidx[(0,a)]]-=1
        if b!=0: v[eidx[(0,b)]]+=1
        rows.append(v)
    C=sp.Matrix(rows); Cpinv=C.T*(C*C.T).inv()
    return edges,eidx,C,Cpinv

def rep(p,edges,eidx,C,Cpinv):
    m=len(edges); P=sp.zeros(m,m)
    for j,(a,b) in enumerate(edges):
        pa,pb=p[a],p[b]; e2=(pa,pb) if pa<pb else (pb,pa); P[eidx[e2],j]=1
    return C*P*Cpinv

def cyc_type(g,nv):
    seen=[False]*nv;parts=[]
    for s in range(nv):
        if seen[s]:continue
        l=0;x=s
        while not seen[x]:seen[x]=True;x=g[x];l+=1
        parts.append(l)
    return tuple(sorted([c for c in parts if c>1],reverse=True)) or (1,)

def study(n):
    nv=n+1; dim=comb(n,2)
    edges,eidx,C,Cpinv=cyc_setup(nv); I=sp.eye(dim)
    print(f"\n=== rung {n}: S{nv} on cycle space dim {dim} ===")
    # all double-transpositions (V2 elements = (2,2) cycle type)
    v2s=[]
    for p in permutations(range(nv)):
        if cyc_type(p,nv)==(2,2):
            v2s.append(p)
    # dedup as set
    v2s=list(dict.fromkeys(v2s))
    print(f"  #(2,2) double-transpositions: {len(v2s)}")
    # study each distinct one's cycle-space action
    seen_action={}
    for g in v2s:
        T=rep(g,edges,eidx,C,Cpinv)
        key=tuple(T)
        if key in seen_action: 
            seen_action[key][1].append(g); continue
        T2=sp.simplify(T*T-I)
        isinv = T2==sp.zeros(dim,dim)
        ev=T.eigenvals()  # dict eigenvalue->mult
        evs={sp.nsimplify(k):v for k,v in ev.items()}
        seen_action[key]=[ (g, isinv, evs), [g] ]
    print(f"  distinct cycle-space actions among the (2,2)'s: {len(seen_action)}")
    for (g,isinv,evs),members in seen_action.values():
        print(f"    e.g. {g}: T^2=I? {isinv}  eigenvalues {evs}  (#perms with this action: {len(members)})")
    # COMMUTATION: do two distinct V2 actions commute on cycle space?
    actions=[ (info[0], rep(info[0],edges,eidx,C,Cpinv)) for info,_ in seen_action.values() ]
    print(f"  --- commutation of distinct V2 cycle-space actions ---")
    noncommuting=0; commuting=0
    for i in range(len(actions)):
        for jx in range(i+1,len(actions)):
            A=actions[i][1]; B=actions[jx][1]
            if sp.simplify(A*B-B*A)==sp.zeros(dim,dim): commuting+=1
            else: noncommuting+=1
    print(f"    commuting pairs: {commuting}, NON-commuting pairs: {noncommuting}")
    return seen_action

for n in (2,3,4):
    study(n)
