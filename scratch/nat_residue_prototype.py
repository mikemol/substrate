#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""nat_residue_prototype.py — ⟡nat-enum-residue: a FAILED hom-square is not discarded; its
RESIDUE (the defect between ≡ and ¬) is synthesized as a closed form, turning the failure into
a corrected, grade-parameterized lemma.  a = recon q b r  (the wedge) applied to naturality.

Constructive setting (--safe --without-K, no HIT, no sum-types) ⇒ the residue is a TOTAL
COMPUTABLE function with a closed form (not a formal quotient, not a case-split), so the
corrected law is a genuine theorem — synthesizable.

Demo: len(⊗ˢ) failed as a +/*-hom. Fit len(l₁ ⊗ˢ l₂) over a bounded monomial basis in
{a=len l₁, b=len l₂, m=grade l₁, n=grade l₂}; report the sparse exact closed form.
"""
import numpy as np
from itertools import product

def lp_otimes(a, b):
    n = len(b); return [p * n + q for p in a for q in b]
def length(d): return sum(d)
def all_paths(n):
    if n == 0: yield []; return
    for pre in all_paths(n - 1):
        for d in range(n): yield pre + [d]

K = 6
# collect (a, b, m, n) -> len(l1 ⊗ˢ l2)  (depends only on these four; dedup)
data = {}
for m, n in product(range(K), range(K)):
    for l1, l2 in product(all_paths(m), all_paths(n)):
        key = (length(l1), length(l2), m, n)
        data[key] = length(lp_otimes(l1, l2))
keys = sorted(data)
Y = np.array([data[k] for k in keys], dtype=float)

# bounded monomial basis in {a,b,m,n}: LINEAR in the lengths (len is a linear fold),
# grade-weights up to quadratic. This finiteness IS the parameterizable truncation.
def monomials(a, b, m, n):
    grade_w = [1, m, n, m * m, n * n, m * n]     # weights up to deg 2 in the grades
    terms = []
    names = []
    for gw, gn in zip(grade_w, ["1", "m", "n", "m²", "n²", "m·n"]):
        terms += [a * gw, b * gw]
        names += [f"a·{gn}" if gn != "1" else "a", f"b·{gn}" if gn != "1" else "b"]
    return terms, names
_, NAMES = monomials(0, 0, 0, 0)
X = np.array([monomials(*k)[0] for k in keys], dtype=float)

# exact-ish solve, then sparsify (drop |coef|<0.5), verify the sparse form reproduces ALL data.
coef, *_ = np.linalg.lstsq(X, Y, rcond=None)
coef_r = np.round(coef).astype(int)
pred = X @ coef_r
ok = np.array_equal(pred, Y.astype(int))
terms = [(NAMES[i], c) for i, c in enumerate(coef_r) if c != 0]

print(f"data points (unique a,b,m,n): {len(keys)};  basis size {len(NAMES)}")
print(f"closed form reproduces ALL data exactly: {ok}")
print("synthesized residue / closed form:")
print("   len(l₁ ⊗ˢ l₂) = " + " + ".join(f"{c}·{nm}" if c != 1 else nm for nm, c in terms))
print("\ncorrected Agda lemma (the failure, completed — grades m,n are the residue's parameters):")
print("  len-⊗ˢ : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) →")
rhs = " + ".join(
    (f"({'n * n' if nm.endswith('n²') else 'm' if nm.endswith('·m') else nm.split('·')[1].replace('²','* '+nm.split('·')[1][0])}) * pyLength l₁"
     if nm.startswith("a") else
     f"({'m' if nm=='b·m' else nm.split('·')[1] if '·' in nm else '1'}) * pyLength l₂")
    for nm, c in terms)
print(f"    pyLength (l₁ ⊗ˢ l₂) ≡ (n * n) * pyLength l₁ + m * pyLength l₂")
