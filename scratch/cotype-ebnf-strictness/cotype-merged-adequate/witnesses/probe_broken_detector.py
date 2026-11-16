# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# Focused: a divide-and-break multiplicity detector returns 0 where factor-and-match returns the true
# multiplicity — the bug that was believed over a correct witness. Demonstrates the failure directly.
import os,sys; sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import species_store as s, sympy as sp
from sympy import symbols, Poly, cyclotomic_poly, factor_list, div, totient
x=symbols('x')
def build_c(c,p,nv):
    perm=list(range(nv))
    for j in range(c):
        cyc=list(range(j*p,(j+1)*p))
        for i in range(p): perm[cyc[i]]=cyc[(i+1)%p]
    return tuple(perm)
p,c,nv=3,3,9
edges,eidx,C,Cp=s.cyc_setup(nv); T=s.rep(build_c(c,p,nv),edges,eidx,C,Cp)
cp=Poly(T.charpoly(x).as_expr(),x); Phi=Poly(cyclotomic_poly(p,x),x)
# BROKEN: divide-and-break
broken=0; q=cp
while q.degree()>=Phi.degree():
    quo,r=div(q,Phi,x)
    if r==Poly(0,x): q=quo; broken+=1
    else: break
# CORRECT: factor-and-match
_,fl=factor_list(cp.as_expr(),x)
correct=sum(m for f,m in fl if Poly(f,x).monic()==Phi.monic())
print(f"(3,3,3): broken divide-break detector = {broken}, correct factor-match = {correct}")
print(f"the bug: {broken} != {correct}. Believing the broken 0 over the witness was the error.")
sys.exit(0 if (broken==0 and correct>0) else 1)  # PASS = the bug is demonstrated (broken wrong, correct right)
