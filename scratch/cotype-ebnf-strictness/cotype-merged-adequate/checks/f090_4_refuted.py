# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import sys, os, json, importlib.util
HERE=os.path.dirname(os.path.realpath(__file__)); ROOT=os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT,'witnesses'))
spec=importlib.util.spec_from_file_location('probe_inv_cheap', os.path.join(ROOT,'witnesses','probe_inv_cheap.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
gold=json.load(open(os.path.join(ROOT,'data','f090_4_refuted' + '_gold.json')))
bad=[]
for (p,c) in m.CASES:
    nv=c*p
    mult,_,_=m.phi_mult_cheap(m.build_c(c,p,nv),nv,p)
    exp=gold.get("{},{}".format(p,c))
    if exp != int(mult):
        bad.append(("{},{}".format(p,c), int(mult), exp))
if bad:
    print("MISMATCH for claim f090_4_refuted:", bad[0]); sys.exit(1)
print("claim f090_4_refuted: live recompute matches committed gold (inv_cheap)"); sys.exit(0)
