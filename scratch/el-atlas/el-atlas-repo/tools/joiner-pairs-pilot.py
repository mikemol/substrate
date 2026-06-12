#!/usr/bin/env python3
"""W2: the two waiting joiner pairs, one stratum down.
{LOC,L26}: witness sets over (lock, probe) cells — per-cell failure
signatures compared mechanically. {PUR,PRO}: the collapse family
(p, lam*p) read twice — as PUR's falsification instance under pinned
norm and as PRO's truth instance from the free model."""
import math
TOL=1e-9
def locus(u,lk):
    if lk in ('available','forced'): return (u,-u)
    if lk=='wrong': return (u,-2*u)
    if lk=='affine': return (u,-u+0.3)
    return None
LOCKS=['available','forced','wrong','affine']   # mutually statable for both claims
US=[-2.0,0.5,1.0]
loc_fail=set(); l26_fail=set()
for lk in LOCKS:
    for u in US:
        p=locus(u,lk); q=locus(-u,lk)
        if abs(sum(p))>=TOL: loc_fail.add((lk,u))
        if not (abs(p[1]-q[0])<TOL and abs(p[0]-q[1])<TOL): l26_fail.add((lk,u))
print("== {LOC,L26} ==")
print("LOC failure cells:", sorted(loc_fail))
print("L26 failure cells:", sorted(l26_fail))
if loc_fail==l26_fail: rel="EQUAL witness sets"
elif loc_fail<l26_fail: rel="LOC strictly contained in L26"
elif l26_fail<loc_fail: rel="L26 strictly contained in LOC"
else:
    rel=f"INCOMPARABLE: LOC-only {sorted(loc_fail-l26_fail)}, L26-only {sorted(l26_fail-loc_fail)}"
print("relation:", rel)
# algebraic check of the suspected identity: sum(p)=0 iff swap-antisymmetry, on linear loci
# locus(u)=(u, f(u)); L26 compares (f(u) - (-u_dual))... verify pointwise equivalence cell-by-cell:
agree=all(((lk,u) in loc_fail)==((lk,u) in l26_fail) for lk in LOCKS for u in US)
print("cell-by-cell verdict agreement:", agree)
print()
print("== {PUR,PRO} ==")
fam=[((3.0,4.0),2.0),((1.0,2.0),3.0),((5.0,12.0),0.5)]
ok_pur=ok_pro=True; rows=[]
for p,lam in fam:
    q=(lam*p[0],lam*p[1])
    n=lambda v: (v[0]/math.hypot(*v), v[1]/math.hypot(*v))
    collapsed = (abs(n(p)[0]-n(q)[0])<TOL and abs(n(p)[1]-n(q)[1])<TOL)        # PUR falsification instance (pinned)
    distinct  = (math.hypot(*p)!=math.hypot(*q))                                # PRO truth instance (free double-entry)
    rows.append((p,q,collapsed,distinct))
    ok_pur &= collapsed; ok_pro &= distinct
for p,q,c,d in rows: print(f"  {p} ~ {q}: pinned-collapse={c}  free-distinct={d}")
print("same family witnesses BOTH readings (bijection = identity on the family):", ok_pur and ok_pro)
print("classification: ISO-WITH-REFRAMING — PUR's falsification witnesses and PRO's truth witnesses")
print("are the SAME collision family, read from pinned vs free models (PR2's exhibit family is the shared carrier).")
