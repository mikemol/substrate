# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import sys, os, re, importlib.util
HERE=os.path.dirname(os.path.realpath(__file__)); ROOT=os.path.dirname(HERE)
KEY="f090_2_pinned"
src=open(os.path.join(ROOT,"warrants.bib")).read()
claim=re.sub(r'\s+',' ',re.search(r'@misc\{'+re.escape(KEY)+r',(.*?)\n\}',src,re.S).group(1))
# the claim must assert the (p-1)/2 multiplicity formula for two p-cycles (c=2)
if not re.search(r'mult\s*=\s*\(?p[−-]1\)?/2', claim):
    print(f"{KEY}: prose no longer asserts mult=(p-1)/2"); sys.exit(1)
sys.path.insert(0, os.path.join(ROOT,"witnesses"))
spec=importlib.util.spec_from_file_location("probe_inv_cheap", os.path.join(ROOT,"witnesses","probe_inv_cheap.py"))
pr=importlib.util.module_from_spec(spec); spec.loader.exec_module(pr)
# verify c=2 cases: probe's mult == (p-1)/2 for each odd p in CASES
bad=[]
for (p,c) in pr.CASES:
    if c!=2: continue
    mult,_,_=pr.phi_mult_cheap(pr.build_c(c,p,c*p),c*p,p)
    want=(p-1)//2
    if int(mult)!=want and p!=2: bad.append((p,int(mult),want))
if bad: print(f"PROSE!=COMPUTE {KEY}: p={bad[0][0]} probe={bad[0][1]} (p-1)/2={bad[0][2]}"); sys.exit(1)
print(f"{KEY}: prose-asserted mult=(p-1)/2 verified for c=2 cases"); sys.exit(0)
