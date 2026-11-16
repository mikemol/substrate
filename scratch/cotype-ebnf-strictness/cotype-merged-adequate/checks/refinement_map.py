# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import sys, os, json
HERE=os.path.dirname(os.path.realpath(__file__)); ROOT=os.path.dirname(HERE)
gold=json.load(open(os.path.join(ROOT,'data','refinement_gold.json')))
# recompute from the committed source-of-truth routings stored next to the data
kw=json.load(open(os.path.join(ROOT,'data','kw_routing.json')))
tr=json.load(open(os.path.join(ROOT,'data','tr_routing.json')))
from collections import defaultdict, Counter
r=defaultdict(Counter)
for k,t in zip(kw,tr): r[k]+=Counter([t])
live={sec:dict(c) for sec,c in r.items()}
if live != gold:
    print("REFINEMENT DRIFT:", {k:(live.get(k),gold.get(k)) for k in set(live)|set(gold) if live.get(k)!=gold.get(k)}); sys.exit(1)
print("refinement map holds: keyword spine refines onto T1/T2/T3 exactly as committed"); sys.exit(0)
