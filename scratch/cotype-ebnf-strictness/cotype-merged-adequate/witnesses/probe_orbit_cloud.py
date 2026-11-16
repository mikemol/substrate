# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# Search the RIGHT event: not kernel collapse, but a frame-collision degeneracy.
# A collision M·p0 == M·p1 means g = p1∘p0^-1 satisfies M_g acting trivially on the
# ORBIT POINT (the generic cycle-space vector image), even if M_g != I globally.
# Equivalent test: does some nontrivial g have M_g fixing the orbit-defining data?
#
# Cleanest faithful-to-rung-3 test: a collision exists iff two frames give the same
# cycle-space MAP. We already know (generator test) the rep is INJECTIVE as a group
# rep through rung 12 -> so M_g == I only for g == e. Therefore NO two frames give the
# same matrix at rungs 4-12. So the rung-3 "22" event (two frames same map) genuinely
# does NOT recur as a same-MAP collision either -- the original probe's 22 was M_{p0}=M_{p1}.
#
# BUT the user's claim is subtler: a TWISTED reflection-degeneracy. The place that can
# live, given injectivity, is the ORBIT CLOUD of a FIXED generic vector v: distinct maps
# M can still send a *particular* v to the same point (M0 v == M1 v with M0 != M1).
# That is the actual "orbit cloud < |group|" phenomenon. Test THAT, on a generic v,
# but reuse: orbit collision M0 v == M1 v  <=>  (M0^-1 M1) v == v  <=> g=... fixes v.
# So: count stabilizer of a generic v. For rung 3 the stabilizer of generic v is
# nontrivial (size 24/22 isn't integer -> the cloud is 22 because 2 PAIRS coincide,
# i.e. exactly 2 nontrivial elements fix v). Search nontrivial elements fixing a
# generic v, classify them.
import sys, sympy as sp
from itertools import combinations, permutations
from math import comb
from fractions import Fraction
import random

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
    Cf=[[Fraction(int(C[i,j].p),int(C[i,j].q)) for j in range(C.cols)] for i in range(C.rows)]
    Pf=[[Fraction(int(Cpinv[i,j].p),int(Cpinv[i,j].q)) for j in range(Cpinv.cols)] for i in range(Cpinv.rows)]
    return edges, eidx, Cf, Pf

def matvec(A,x):  # A (dim x dim) times x (len dim)
    return [sum(A[i][t]*x[t] for t in range(len(x))) for i in range(len(A))]
def matmul(A,B):
    n=len(A);m=len(B[0]);k=len(B)
    return [[sum(A[i][t]*B[t][j] for t in range(k)) for j in range(m)] for i in range(n)]
def rep_matrix(p, edges, eidx, Cf, Pf):
    dim=len(Cf); m=len(edges)
    CE=[[Fraction(0)]*m for _ in range(dim)]
    for j,(a,b) in enumerate(edges):
        pa,pb=p[a],p[b]; e2=(pa,pb) if pa<pb else (pb,pa); jj=eidx[e2]
        for i in range(dim): CE[i][jj]=Cf[i][j]
    return matmul(CE,Pf)

def cyc_type(g,nv):
    seen=[False]*nv; parts=[]
    for s in range(nv):
        if seen[s]:continue
        l=0;x=s
        while not seen[x]: seen[x]=True;x=g[x];l+=1
        parts.append(l)
    return tuple(sorted([c for c in parts if c>1],reverse=True)) or (1,)

def orbit_stabilizer(n, vseed=12345):
    """Count nontrivial group elements fixing a GENERIC integer vector v in cycle space.
       Orbit-cloud size = |group| - (#elements fixing v beyond identity collapses)."""
    nv=n+1; dim=comb(n,2)
    edges,eidx,Cf,Pf=cyc_setup(nv)
    rng=random.Random(vseed)
    v=[Fraction(rng.randint(1,97)) for _ in range(dim)]   # generic rational vector
    images={}
    fixers=[]   # nontrivial g with M_g v == v
    distinct=0
    for p in permutations(range(nv)):
        M=rep_matrix(p,edges,eidx,Cf,Pf)
        w=tuple(matvec(M,v))
        if w in images:
            # p and images[w] send v to same point -> g = p ∘ images[w]^-1 fixes v
            p0=images[w]
            inv0=[0]*nv
            for i,x in enumerate(p0): inv0[x]=i
            g=tuple(p[inv0[i]] for i in range(nv))
            fixers.append(g)
        else:
            images[w]=p; distinct+=1
    return nv,dim,len(images),distinct,fixers,edges,eidx,Cf,Pf

def classify_fixers(fixers,nv,edges,eidx,Cf,Pf,dim):
    from collections import Counter
    I=[[Fraction(1 if i==j else 0) for j in range(dim)] for i in range(dim)]
    out=Counter()
    for g in set(fixers):
        M=rep_matrix(g,edges,eidx,Cf,Pf)
        # is M == I ? (kernel)  is M^2==I (involution/idempotent)?  nilpotent N=M-I?
        isI=all(M[i][j]==I[i][j] for i in range(dim) for j in range(dim))
        M2=matmul(M,M)
        invol=all(M2[i][j]==I[i][j] for i in range(dim) for j in range(dim))
        # nilpotency of N=M-I
        N=[[M[i][j]-I[i][j] for j in range(dim)] for i in range(dim)]
        Nk=N; nidx=None
        for k in range(1,dim+2):
            if all(Nk[i][j]==0 for i in range(dim) for j in range(dim)): nidx=k; break
            Nk=matmul(Nk,N)
        ct=cyc_type(g,nv)
        kind=("KERNEL(M=I)" if isI else "idempotent/involution(T^2=I)" if invol
              else f"NILPOTENT(N^{nidx}=0)" if nidx else "OTHER")
        out[(ct,kind)]+=1
    return dict(out)

if __name__=="__main__":
    lo=int(sys.argv[1]); hi=int(sys.argv[2])
    for n in range(lo,hi+1):
        nv,dim,nimg,distinct,fixers,edges,eidx,Cf,Pf=orbit_stabilizer(n)
        import math
        print(f"rung {n}: K{nv} cyc-dim {dim} | frames {math.factorial(nv)} -> orbit-cloud {distinct} | nontrivial fixers of generic v: {len(fixers)}", flush=True)
        if fixers:
            cls=classify_fixers(fixers,nv,edges,eidx,Cf,Pf,dim)
            print(f"        species of the reroute: {cls}", flush=True)
