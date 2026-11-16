# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import sys, os, json
HERE=os.path.dirname(os.path.realpath(__file__)); ROOT=os.path.dirname(HERE)
g=json.load(open(os.path.join(ROOT,'data','bridge_projection_identity.json')))['projection_identity']
cot=open(os.path.join(ROOT,'cotype.md')).read(); L=cot.split(chr(10)); E=4136
sig=chr(10).join(L[:E]); fr=chr(10).join(L[E:])
if g['sigma_anchor'] not in sig: print("MISS sigma:", g['sigma_anchor']); sys.exit(1)
if g['frob_anchor'] not in fr: print("MISS frob:", g['frob_anchor']); sys.exit(1)
print("projection_identity: " + g['claim']); sys.exit(0)
