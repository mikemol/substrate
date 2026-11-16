# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# P-INV-COND: Φ_p multiplicity = f(#p-cycles, p) via numeric nullity, SYMPY-FREE.
# Uses species_np (numpy frame) + closed-form Φ_p for prime p. No symbolic charpoly/factor, no sympy
# import — ~0.1s fixed cost vs ~0.32s. Identical results, verified vs species_store to 1e-9.
import os,sys; sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import species_np as snp

def build_c_pcycles(c,p,nv):
    perm=list(range(nv))
    for j in range(c):
        cyc=list(range(j*p,(j+1)*p))
        for i in range(p): perm[cyc[i]]=cyc[(i+1)%p]
    return tuple(perm)

import json as _json
CASES=[(2,2),(2,3),(2,4),(3,1),(3,2),(3,3),(3,4),(5,1),(5,2),(7,1)]
def compute(case):
    p,c=case; nv=c*p
    return int(snp.phi_mult(build_c_pcycles(c,p,nv),nv,p))
_gp=os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','data','inv_cond_count_gold.json')
try: GOLD={k: v for k,v in _json.load(open(_gp)).items()}
except Exception: GOLD=None
def fmt(case,res): return f"p={case[0]} c={case[1]} -> Phi_p mult={res}"
from pump_adapter import make, run_main
initial,pump,parse,serialize,deserialize = make(globals())
if __name__=="__main__": run_main(globals())
