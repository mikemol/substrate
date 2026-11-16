# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import sys, os, re, importlib.util
HERE=os.path.dirname(os.path.realpath(__file__)); ROOT=os.path.dirname(HERE)
KEY="f089_1_data"

# 1. READ THE CLAIM PROSE from warrants.bib (this is what couples the check to the paper's content)
src=open(os.path.join(ROOT,"warrants.bib")).read()
m=re.search(r'@misc\{'+re.escape(KEY)+r',(.*?)\n\}', src, re.S)
claim=re.search(r'claim\s*=\s*\{(.+?)\}', m.group(1), re.S).group(1)
claim=re.sub(r'\s+',' ',claim)

# 2. PARSE the asserted (p,c)->mult table out of the prose
asserted={}
for seg in re.finditer(r'p=(\d+):\s*c=([\d.,]+(?:\.\.\d+)?)\s*[→-]+\s*([\d,]+)', claim):
    p=int(seg.group(1)); crange=seg.group(2); mults=[int(x) for x in seg.group(3).split(',')]
    if '..' in crange:
        a,b=crange.split('..'); cs=list(range(int(a),int(b)+1))
    else:
        cs=[int(x) for x in crange.split(',')]
    for c,mult in zip(cs,mults): asserted[(p,c)]=mult
if not asserted:
    print("PROSE-BIND FAIL: no table parsed from claim"); sys.exit(1)

# 3. RECOMPUTE live via the probe (pump API) and verify against the PROSE-asserted numbers
sys.path.insert(0, os.path.join(ROOT,"witnesses"))
spec=importlib.util.spec_from_file_location("probe_inv_cond_count", os.path.join(ROOT,"witnesses","probe_inv_cond_count.py"))
pr=importlib.util.module_from_spec(spec); spec.loader.exec_module(pr)
bad=[]
for (p,c),want in asserted.items():
    got=pr.compute((p,c))
    if got != want: bad.append(((p,c),got,want))
if bad:
    print(f"PROSE!=COMPUTE for {KEY}: {bad[0]}  (prose says {bad[0][2]}, probe computes {bad[0][1]})"); sys.exit(1)
print(f"{KEY}: prose-asserted table {sorted(asserted.items())[:3]}... reproduced by live probe ({len(asserted)} cells)"); sys.exit(0)
