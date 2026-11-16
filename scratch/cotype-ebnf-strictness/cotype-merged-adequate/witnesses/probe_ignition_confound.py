# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import species_store as s
import sympy as sp
import random
db=s.connect()
def perm_pow(p,e):
    r=tuple(range(len(p)))
    for _ in range(e): r=tuple(p[r[i]] for i in range(len(p)))
    return r

# CONFOUND CHECK 1: is (3,3,3) singular AT ALL at nv=9? sample direct (3,3,3) elements.
nv=9; edges,eidx,C,Cpinv=s.cyc_setup(nv)
print(f"=== nv={nv}: is the (3,3,3) species singular at all? (direct sample) ===", flush=True)
random.seed(2); found=0; sing=0; tries=0
seen=set()
while found<20 and tries<4000:
    tries+=1
    perm=list(range(nv)); random.shuffle(perm); perm=tuple(perm)
    if s.cyc_type(perm,nv)==(3,3,3) and perm not in seen:
        seen.add(perm); found+=1
        T=s.rep(perm,edges,eidx,C,Cpinv)
        if sp.cancel(T.det())==0: sing+=1
print(f"  sampled {found} direct (3,3,3) elements: {sing} singular  (fraction {sing/max(found,1):.3f})")

# CONFOUND CHECK 2: also test (3,3,3) at nv=6 (where order-3 IGNITES, known hot) as a
# positive control -- does the 3->? structure show composed there?
nv6=6; e6,ix6,C6,Cp6=s.cyc_setup(nv6)
print(f"=== positive control nv={nv6}: (3,3) singular fraction (known-hot order-3) ===", flush=True)
import itertools
n33=0; s33=0
for perm in itertools.permutations(range(nv6)):
    if s.cyc_type(perm,nv6)==(3,3):
        n33+=1
        T=s.rep(perm,e6,ix6,C6,Cp6)
        if sp.cancel(T.det())==0: s33+=1
print(f"  (3,3) at nv=6: {s33}/{n33} singular = {s33/n33:.3f}")

# CONFOUND CHECK 3: widen p=3 ascent sample -- 60 nine-cycles, count cube-singular
nv9=9
print(f"=== p=3 ascent widened: 60 nine-cycles @ nv={nv9}, cube singular? ===", flush=True)
random.seed(3); comp=0; prim=0; ch=0
base=tuple(list(range(1,nv9))+[0])
while ch<60:
    perm=list(range(nv9)); random.shuffle(perm)
    inv=[0]*nv9
    for i,x in enumerate(perm): inv[x]=i
    g=tuple(perm[base[inv[i]]] for i in range(nv9))
    if s.cyc_type(g,nv9)!=(9,): continue
    cube=perm_pow(g,3); 
    T=s.rep(cube,edges,eidx,C,Cpinv)
    if sp.cancel(T.det())==0: comp+=1
    else: prim+=1
    ch+=1
print(f"  {ch} nine-cycles: composed(cube-singular) {comp}, primitive {prim}, frac {comp/ch:.3f}")
db.close()
