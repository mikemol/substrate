# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# Is the coboundary tower a CLEAN Horner fold (power map P the same shape at every
# prime/digit) or a TWISTED one (P varies per rung, like the cocycle's ε)?
#
# Test: the composed-injection is "lower rung pulled up by the p-th power map".
#   order-4 (p=2, 2->4): composed 4-cycles are those whose SQUARE is a singular (2,2).
#   order-9 (p=3, 3->9): composed 9-cycles are those whose CUBE is a singular (3,3).
# Compare the STRUCTURE of the power map at the two primes:
#   - fraction composed (does the split ratio match across primes? clean Horner -> same)
#   - does the composed cell's spectrum = (lower cell spectrum) acted on by P uniformly?
# We can do p=2 (order-4 @ nv=8, already have 28 singular (4)-cycles in the store)
# cheaply. p=3 order-9 needs nv=9 (rung 8) -- heavier; do a TARGETED version:
# only the (9) and (9,9)... actually (9) needs nv>=9 so nv=9 (rung 8, 9!), too big to
# enumerate. Instead test p=3 at the SMALLEST place a 9-structure's cube-content shows:
# use order-6 = 2*3 (nv=6, rung 5, already have data) as the MIXED-radix probe, which
# is the sharper Horner discriminator anyway (two nontrivial digits).
import species_store as s
import sympy as sp
db=s.connect()

def powmap(p,k): return tuple(p[k] for k in range(len(p)))  # placeholder
def perm_pow(p, e):
    r=tuple(range(len(p)))
    for _ in range(e): r=tuple(p[r[i]] for i in range(len(p)))
    return r

# ---- p=2 power map at order-4 (the 2->4 ascent), nv=8 ----
nv=8; edges,eidx,C,Cpinv=s.cyc_setup(nv)
sing4=db.execute("SELECT perm FROM residue WHERE rung=7 AND mechanism='order-4' AND singular=1 AND cyc_type='(4,)'").fetchall()
comp=0; prim=0
for (ps,) in sing4:
    p=tuple(map(int,ps.split(',')))
    sq=perm_pow(p,2)
    T=s.rep(sq,edges,eidx,C,Cpinv)
    if sp.cancel(T.det())==0: comp+=1
    else: prim+=1
tot2=comp+prim
print(f"p=2 ascent (2->4) @ nv=8: composed {comp}/{tot2} = {comp/tot2:.3f}, primitive {prim}/{tot2} = {prim/tot2:.3f}")

# ---- p=3 ascent: need order-9 content. Smallest carrier with a 9-cycle is nv=9 (rung8).
# Too big to enumerate fully; instead test the (3,3,3) -> does its structure ascend like
# (2,2)->(4)? Use nv=9 but ONLY build a few representative 9-cycles and 3-power them.
nv3=9
print(f"p=3 ascent (3->9) @ nv={nv3}: building targeted reps (9-cycles, cube = (3,3,3))...", flush=True)
edges3,eidx3,C3,Cp3=s.cyc_setup(nv3)
# a 9-cycle: (0 1 2 3 4 5 6 7 8); its cube is (0 3 6)(1 4 7)(2 5 8) = a (3,3,3)
import itertools, random
random.seed(1)
reps=[]
base=tuple(list(range(1,nv3))+[0])  # the 9-cycle (0 1 2 ... 8)
# generate a handful of 9-cycles by conjugation
for _ in range(12):
    perm=list(range(nv3)); random.shuffle(perm)
    inv=[0]*nv3
    for i,x in enumerate(perm): inv[x]=i
    g=tuple(perm[base[inv[i]]] for i in range(nv3))  # conjugate of base
    reps.append(g)
comp3=0; prim3=0; checked=0
for g in reps:
    if s.cyc_type(g,nv3)!=(9,): continue
    cube=perm_pow(g,3)            # should be (3,3,3)
    T=s.rep(cube,edges3,eidx3,C3,Cp3)
    sing = sp.cancel(T.det())==0
    if sing: comp3+=1
    else: prim3+=1
    checked+=1
print(f"  checked {checked} 9-cycles: cube-singular(composed) {comp3}, cube-nonsingular(primitive) {prim3}")
if checked:
    print(f"  p=3 composed fraction = {comp3/checked:.3f}")
print()
print("CLEAN Horner predicts the composed FRACTION ~matches across primes (same power-map shape).")
print("TWISTED predicts the fraction DIFFERS per prime (P varies per rung, cocycle-style).")
db.close()
