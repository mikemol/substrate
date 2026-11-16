# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# CLIMB-CHECK the arity result: does "3 gains structural ramification on 2-faces (triangles)" hold
# across elements/carriers, or is (4,2)@nv=6 a single-rung coincidence? Compare k=1 (edges) vs k=2
# (triangles) for several elements; track whether 3's ramification is suppressed at k=1 and present at k=2.
import os,sys; sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
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
    n=abs(int(n))
    if n==0: return None
    v=0
    while n%p==0: n//=p; v+=1
    return v
def setup_k(nv,k):
    faces=list(combinations(range(nv),k)); fidx={f:i for i,f in enumerate(faces)}
    tree=set(f for f in faces if 0 in f); rows=[]
    for f in faces:
        if f in tree: continue
        v=[0]*len(faces); v[fidx[f]]+=1
        for i in range(k):
            sub=f[:i]+f[i+1:]; fill=tuple(sorted((0,)+sub))
            if 0 in sub: continue
            if fill in fidx and fill in tree: v[fidx[fill]]+=(-1)**i
        rows.append(v)
    C=sp.Matrix(rows)
    if C.rows==0: return None,None,None,None
    return faces,fidx,C,C.T*(C*C.T).inv()
def rep_k(perm,faces,fidx,C,Cpinv):
    m=len(faces);P=sp.zeros(m,m)
    for j,f in enumerate(faces):
        pf=tuple(sorted(perm[v] for v in f)); P[fidx[pf],j]=1
    return C*P*Cpinv
def primes_ramified(T,primes=tuple(primerange(2,20))):
    cp=Poly(T.charpoly(x).as_expr(),x); _,fl=factor_list(cp.as_expr(),x)
    agg={}
    for f,m in fl:
        fp=Poly(f,x);kk=None
        for c in range(1,30):
            if Poly(cyclotomic_poly(c,x),x).monic()==fp.monic():kk=c;break
        if kk is None and fp.degree()>=2:
            ld=1
            for cc in fp.all_coeffs(): ld=sp.lcm(ld,sp.denom(sp.nsimplify(cc)))
            Pint=Poly(sp.expand(fp.as_expr()*ld),x)
            try:
                disc=Pint.discriminant()
                for p in primes:
                    val=vp(disc,p)
                    if val: agg[p]=agg.get(p,0)+val
            except: pass
    return agg
# CASES: (label, cycle-spec, nv). PUMP-COMPATIBLE via pump_adapter; one element per increment.
CASES=[("(4,2)@6",[[0,1,2,3],[4,5]],6),("(3,2)@6",[[0,1,2],[3,4]],6),
       ("(2,2)@6",[[0,1],[2,3]],6),("(5)@6",[[0,1,2,3,4]],6),("(3,3)@6",[[0,1,2],[3,4,5]],6)]

def compute(case):
    name,cyc,nv=case
    perm=build([tuple(c) for c in cyc],nv); row={}
    for k in [1,2]:
        fc,fi,C,Cp=setup_k(nv,k)
        row[k]= None if fc is None else primes_ramified(rep_k(perm,fc,fi,C,Cp))
    # verdict content: v3 present at k=2; gains relative to k=1 (or appears where absent at k=1)
    v3_k1=(row[1] or {}).get(3,0); v3_k2=(row[2] or {}).get(3,0)
    def pairs(d): return sorted([[int(k),int(v)] for k,v in (d or {}).items()])
    return {"k1":pairs(row[1]),"k2":pairs(row[2]),"v3_k1":int(v3_k1),"v3_k2":int(v3_k2),
            "v3_gains": bool(v3_k2>v3_k1)}

def fmt(case,res):
    d=lambda L: "{"+", ".join(f"{p}:{v}" for p,v in L)+"}"
    return f"  {case[0]}: k=1 {d(res['k1'])}  |  k=2 {d(res['k2'])}"

from pump_adapter import make
initial,pump,parse,serialize,deserialize = make(globals())

if __name__=="__main__":
    import sys
    st=initial()
    while not parse(st)["done"]: st=pump(st)
    m=parse(st)
    print("CLIMB-CHECK: aggregate v_p(disc), k=1 (edges) vs k=2 (triangles). v3 GAINS on k=2 = arity climb.")
    for case,res in zip(CASES,m["results"]): print(fmt(case,res))
    # family-fact: v3 gains on every element that ramifies at all (degenerate (2,2) may be empty both)
    ramifying=[r for r in m["results"] if r["v3_k1"] or r["v3_k2"] or r["k2"]]
    ok=all(r["v3_gains"] or (not r["k2"]) for r in m["results"]) and any(r["v3_gains"] for r in m["results"])
    print(f"verdict: {'PASS' if ok else 'FAIL'} (v3 systematically gains k=1->k=2; arity=successor)")
    sys.exit(0 if ok else 1)
