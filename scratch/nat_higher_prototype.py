#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""⟡nat-enum-higher — the DISTRIBUTOR coherence (J₃) for maps: does F respect δ (⊗ˢ-over-⊕)?

The two forms differ by the distributor δ (a permutation):
  left  = a ⊗ˢ (b ⊕ c)
  right = (a ⊗ˢ b) ⊕ (a ⊗ˢ c)
For a map F, the coherence is F(left) =? F(right); the RESIDUE (when not) is the higher cell.
"""
import numpy as np
from itertools import product

def punchin(p, x): return x if x < p else x + 1
def insert_at(p, s): return [p] + [punchin(p, v) for v in s]
def decode(d):
    s = []
    for x in d: s = insert_at(x, s)
    return s
def sign(s): return sum(1 for i in range(len(s)) for j in range(i + 1, len(s)) if s[i] > s[j]) & 1
def length(d): return sum(d)
def lp_oplus(a, b): return list(b) + list(a)
def lp_otimes(a, b):
    n = len(b); return [p * n + q for p in a for q in b]
def all_paths(n):
    if n == 0: yield []; return
    for pre in all_paths(n - 1):
        for d in range(n): yield pre + [d]

def left(la, lb, lc):  return lp_otimes(la, lp_oplus(lb, lc))
def right(la, lb, lc): return lp_oplus(lp_otimes(la, lb), lp_otimes(la, lc))

K = 4
GW = [(0,0,0),(1,0,0),(0,1,0),(0,0,1),(2,0,0),(0,2,0),(0,0,2),(1,1,0),(1,0,1),(0,1,1)]  # m,p,q deg≤2
def monos(a, b, c, m, p, q):
    terms, names = [], []
    for (gm, gp, gq) in GW:
        w = m**gm * p**gp * q**gq
        gn = "".join(f"{x}{'' if e==1 else '²'}" for x,e in (("m",gm),("p",gp),("q",gq)) if e) or "1"
        for v, vn in ((a,"a"),(b,"b"),(c,"c")):
            terms.append(v*w); names.append(vn if gn=="1" else f"{vn}·{gn}")
    return terms, names
NAMES = monos(0,0,0,0,0,0)[1]

# ---- len: fit the residue len(left) - len(right) ----
data = {}
for m,p,q in product(range(K),range(K),range(K)):
    for la,lb,lc in product(all_paths(m),all_paths(p),all_paths(q)):
        key=(length(la),length(lb),length(lc),m,p,q)
        data[key]=length(left(la,lb,lc))-length(right(la,lb,lc))
keys=sorted(data); Y=np.array([data[k] for k in keys],float)
X=np.array([monos(*k)[0] for k in keys],float)
cr=np.round(np.linalg.lstsq(X,Y,rcond=None)[0]).astype(int)
ok=np.array_equal(X@cr,Y.astype(int))
terms=[(NAMES[i],int(c)) for i,c in enumerate(cr) if c]
print(f"len   : respects δ on the nose = {all(v==0 for v in data.values())}")
print(f"        residue exact-fit = {ok};  len(left) - len(right) = "
      + (" + ".join(f"{c}·{nm}" for nm,c in terms) or "0"))

# ---- decode: perm-valued — does it respect δ on the nose? ----
dok=all(decode(left(la,lb,lc))==decode(right(la,lb,lc))
        for m,p,q in product(range(3),range(3),range(3))
        for la,lb,lc in product(all_paths(m),all_paths(p),all_paths(q)))
print(f"decode: respects δ on the nose = {dok}  (else: residue = δ itself, the object distributor iso)")

# ---- sign (F₂): is the δ-defect parity always 0? ----
sok=all(sign(decode(left(la,lb,lc)))==sign(decode(right(la,lb,lc)))
        for m,p,q in product(range(K),range(K),range(K))
        for la,lb,lc in product(all_paths(m),all_paths(p),all_paths(q)))
print(f"sign  : respects δ on the nose = {sok}  (= bool→F₂; residue would be sign(δ))")
