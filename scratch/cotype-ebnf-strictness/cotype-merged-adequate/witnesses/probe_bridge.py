# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-BRIDGE, cheap: charpoly roots numerically, map each λ to zeta poles u via q u^2 - λ u + 1 = 0,
# test functional-equation closure u->1/(qu), Ramanujan |λ|<=2√q, critical circle |u|=1/√q.
# PUMP-COMPATIBLE via pump_adapter: one (perm,nv) case per increment; T built inside, never serialized.
import os,sys; sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import species_store as s
import numpy as np
from pump_adapter import make, run_main

def build(cycles,nv):
    p=list(range(nv))
    for cyc in cycles:
        for i in range(len(cyc)): p[cyc[i]]=cyc[(i+1)%len(cyc)]
    return tuple(p)

# CASES: (label, cycle-spec, nv)
CASES=[("(2,3) nv=5",[[0,1],[2,3,4]],5), ("(4,3) nv=7",[[0,1,2,3],[4,5,6]],7)]

def compute(case):
    label,cycles,nv=case; q=nv-2
    edges,eidx,C,Cp=s.cyc_setup(nv)
    T=s.rep(build([tuple(c) for c in cycles],nv),edges,eidx,C,Cp)
    Tn=np.array(T.evalf(),dtype=complex)
    lams=np.linalg.eigvals(Tn)
    rb=2*np.sqrt(q); tempered=int(np.sum(np.abs(lams)<=rb+1e-9))
    poles=[]
    for lam in lams:
        disc=np.sqrt(lam*lam-4*q+0j); poles+=[(lam+disc)/(2*q),(lam-disc)/(2*q)]
    poles=np.array(poles)
    closed=0; checked=0
    for pv in poles:
        if abs(pv)<1e-12: continue
        checked+=1
        if np.min(np.abs(poles-1.0/(q*pv)))<1e-6: closed+=1
    crit=int(np.sum(np.abs(np.abs(poles)-1/np.sqrt(q))<1e-6))
    # verdict content: functional-eq closure total AND all eigs tempered
    return {"dim":int(T.shape[0]),"n_eigs":len(lams),"tempered":tempered,
            "closed":closed,"checked":checked,"crit":crit,"n_poles":len(poles),
            "fe_total": closed==checked, "ramanujan_total": tempered==len(lams)}

# GOLD: the P-BRIDGE finding — functional equation totally closed, every eigenvalue within Ramanujan.
GOLD={repr(c): None for c in CASES}  # structural verdict below instead of value-match
def _verdict_ok(res): return res["fe_total"] and res["ramanujan_total"]

def fmt(case,res):
    label=case[0]
    return (f"{label}: dim={res['dim']} | {res['n_eigs']} eigs, {res['tempered']} within Ramanujan | "
            f"poles closed u→1/(qu): {res['closed']}/{res['checked']} | critical circle: {res['crit']}/{res['n_poles']}")

initial,pump,parse,serialize,deserialize = make(globals())

if __name__=="__main__":
    # cold fallback with the structural verdict (fe + ramanujan total on every case)
    st=initial()
    while not parse(st)["done"]: st=pump(st)
    m=parse(st); ok=all(_verdict_ok(r) for r in m["results"])
    for case,res in zip(CASES,m["results"]): print(fmt(case,res))
    print(f"verdict: {'PASS' if ok else 'FAIL'} (functional-equation + Ramanujan totally closed)")
    sys.exit(0 if ok else 1)
