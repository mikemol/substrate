# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import sys, os, json, importlib.util
HERE=os.path.dirname(os.path.realpath(__file__))
ROOT=os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT,'witnesses'))
spec=importlib.util.spec_from_file_location('probe_inv_cond_count', os.path.join(ROOT,'witnesses','probe_inv_cond_count.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
gold=json.load(open(os.path.join(ROOT,'data','f089_2_solid_gold.json')))
bad=[]
for case in m.CASES:
    res=m.compute(case)
    exp=gold.get(repr(case))
    if exp is None:
        # inv_cheap keys are "p,c" not repr; try compute's own key
        if isinstance(res,(list,tuple)) and len(res)>=2:
            exp=gold.get(f"{res[0]},{res[1]}")
    if exp != res and not (isinstance(res,(list,tuple)) and isinstance(exp,(list,tuple)) and list(res)==list(exp)):
        # last-resort numeric compare for inv_cheap (res=[p,c,mult], gold value=mult)
        if isinstance(res,(list,tuple)) and len(res)==3 and exp==res[2]:
            continue
        bad.append((repr(case), res, exp))
if bad:
    print("MISMATCH for claim f089_2_solid:", bad[0]); sys.exit(1)
print("claim f089_2_solid: live recompute matches committed gold (inv_cond_count)"); sys.exit(0)
