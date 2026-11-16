# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# Faithfulness of the cycle-space rep of S_{n+1} on K_{n+1}, checked on GENERATORS
# instead of by enumerating (n+1)!.  Kernel is a normal subgroup; for n+1>=5 the
# only nontrivial normal subgroups are A_{n+1} and S_{n+1}.  So:
#   * if a 3-cycle is NOT in the kernel  => A_{n+1} not killed => kernel has no
#     even nontrivial elements; combined with a transposition not in kernel =>
#     rep is FAITHFUL.
#   * if a 3-cycle IS in the kernel => A_{n+1} <= kernel => massive collapse
#     (the recurrence, if it exists). Then we enumerate the kernel & classify.
# For n+1=4 (rung 3) S_4 also has V2 normal, so we ALSO check the double
# transposition (0 1)(2 3) directly -- that's the known rung-3 reroute.
import sys, sympy as sp
from itertools import combinations
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
    Cf=[[Fraction(int(C[i,j].p),int(C[i,j].q)) for j in range(C.cols)] for i in range(C.rows)]
    Pf=[[Fraction(int(Cpinv[i,j].p),int(Cpinv[i,j].q)) for j in range(Cpinv.cols)] for i in range(Cpinv.rows)]
    return edges, eidx, Cf, Pf

def matmul(A,B):
    n=len(A); m=len(B[0]); k=len(B)
    return [[sum(A[i][t]*B[t][j] for t in range(k)) for j in range(m)] for i in range(n)]

def rep_matrix(p, edges, eidx, Cf, Pf):
    dim=len(Cf); m=len(edges)
    CE=[[Fraction(0)]*m for _ in range(dim)]
    for j,(a,b) in enumerate(edges):
        pa,pb=p[a],p[b]; e2=(pa,pb) if pa<pb else (pb,pa); jj=eidx[e2]
        for i in range(dim): CE[i][jj]=Cf[i][j]
    return matmul(CE,Pf)

def is_identity(M):
    dim=len(M)
    for i in range(dim):
        for j in range(dim):
            if M[i][j]!=(Fraction(1) if i==j else Fraction(0)): return False
    return True

def perm_from_cycle(nv, *cycles):
    p=list(range(nv))
    for cyc in cycles:
        for i in range(len(cyc)):
            p[cyc[i]]=cyc[(i+1)%len(cyc)]
    return tuple(p)

def faithful_check(n):
    nv=n+1; cyc_dim=comb(n,2)
    edges,eidx,Cf,Pf=cyc_setup(nv)
    # generators: a 3-cycle (0 1 2) tests A_{n+1}; a transposition (0 1) tests parity.
    three=perm_from_cycle(nv,(0,1,2))
    twoc=perm_from_cycle(nv,(0,1))
    M3=rep_matrix(three,edges,eidx,Cf,Pf)
    M2=rep_matrix(twoc,edges,eidx,Cf,Pf)
    three_killed=is_identity(M3)
    two_killed=is_identity(M2)
    extra=""
    if nv==4:  # S4: also test the V2 double-transposition directly
        v2=perm_from_cycle(nv,(0,1),(2,3))
        Mv=rep_matrix(v2,edges,eidx,Cf,Pf)
        extra=f" | V2 (01)(23) killed: {is_identity(Mv)}"
    # verdict
    if three_killed:
        verdict="REROUTE: 3-cycle in kernel => A_{n+1} collapses (recurrence!)"
    elif two_killed:
        verdict="parity reroute: transposition in kernel (sign rep killed)"
    else:
        verdict="FAITHFUL on generators (no 3-cycle, no transposition in kernel)"
    print(f"rung {n}: K{nv} cyc-dim {cyc_dim} | 3-cycle killed: {three_killed} | transposition killed: {two_killed}{extra} -> {verdict}", flush=True)
    return three_killed, two_killed

if __name__=="__main__":
    lo=int(sys.argv[1]); hi=int(sys.argv[2])
    for n in range(lo,hi+1):
        faithful_check(n)
