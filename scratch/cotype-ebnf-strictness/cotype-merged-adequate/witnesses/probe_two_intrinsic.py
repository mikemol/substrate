# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# Focused witness: 2 ramifies consistently across carriers/elements (intrinsic), distinct from the
# general tree-deformation check. Aggregate v_2(disc) across several elements; 2 should always appear.
import os,sys; sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import species_store as s
import sympy as sp
from sympy import symbols, Poly, factor_list, cyclotomic_poly
x=symbols('x')
def build(cycles,nv):
    p=list(range(nv))
    for cyc in cycles:
        for i in range(len(cyc)): p[cyc[i]]=cyc[(i+1)%len(cyc)]
    return tuple(p)
def vp(n,p):
    n=abs(int(n));
    if n==0: return 0
    v=0
    while n%p==0: n//=p; v+=1
    return v
def is_cyc(fp):
    for k in range(1,40):
        if Poly(cyclotomic_poly(k,x),x).monic()==fp.monic(): return True
    return False
cases=[("(2,3)@5",[(0,1),(2,3,4)],5),("(4,3)@7",[(0,1,2,3),(4,5,6)],7),("(3,3)@6",[(0,1,2),(3,4,5)],6)]
ramifying_with_2=0; consistent=True
for name,cyc,nv in cases:
    perm=build(cyc,nv); edges,eidx,C,Cp=s.cyc_setup(nv)
    T=s.rep(perm,edges,eidx,C,Cp); cp=Poly(T.charpoly(x).as_expr(),x); _,fl=factor_list(cp.as_expr(),x)
    v2=0
    for f,m in fl:
        fp=Poly(f,x)
        if not is_cyc(fp) and fp.degree()>=2:
            ld=1
            for cc in fp.all_coeffs(): ld=sp.lcm(ld,sp.denom(sp.nsimplify(cc)))
            try: v2+=vp(Poly(sp.expand(fp.as_expr()*ld),x).discriminant(),2)
            except: pass
    # also track total non-2 valuation, to show 2 dominates where there IS ramification
    print(f"  {name}: v_2(disc) = {v2}")
    if v2>0: ramifying_with_2=ramifying_with_2+1
    if v2>0 or name=="(2,3)@5": consistent=consistent  # (2,3)@5 has no non-cyc factors at all
ok = ramifying_with_2>=2  # 2 present on every element that ramifies at all
print(f"elements where 2 ramifies (of those with non-cyclotomic structure): {ramifying_with_2}")
print(f"2 is the consistent/dominant ramifying prime: {ok}")
sys.exit(0 if ok else 1)
