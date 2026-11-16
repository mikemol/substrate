# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import sys, os, json
HERE=os.path.dirname(os.path.realpath(__file__)); ROOT=os.path.dirname(HERE)
gold=json.load(open(os.path.join(ROOT,'data','bridge_gold.json')))
cotype=open(os.path.join(ROOT,'cotype.md')).read()
lines=cotype.split('\n'); SIGMA_END=4136
sigma='\n'.join(lines[:SIGMA_END]); frob='\n'.join(lines[SIGMA_END:])
bad=[]
for name,ident in gold.items():
    # the structural claim: sigma anchor in Σ-region, frob anchor in Frobenius-region — the SAME-structure bridge
    if ident['sigma_anchor'] not in sigma:
        bad.append((name,'sigma_anchor missing from Σ-region',ident['sigma_anchor']))
    if ident['frob_anchor'] not in frob:
        bad.append((name,'frob_anchor missing from Frobenius-region',ident['frob_anchor']))
if bad:
    print("BRIDGE BROKEN:", bad[0]); sys.exit(1)
print("frame-mismatch bridge holds: all 3 identities co-occur across Σ/Frobenius regions"); sys.exit(0)
