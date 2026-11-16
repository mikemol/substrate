#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""nat_enum_prototype.py — automate the ENUMERATION of tower naturality facts (⟡nat-enum).

A naturality fact is a HOMOMORPHISM SQUARE  F (op_s x y) == op_t (F x) (F y).
`decode-⊕` and `decode-⊗ˢ` (the ones proven by hand) are two INSTANCES of one template
("decode is a monoidal hom"). This enumerates the family:

  candidates = { (F, op_s, op_t) : F ∈ MAPS, (op_s,op_t) type-compatible } — FINITE.
  hold       = numpy-verify each on all finite instances up to grade K.

TRUNCATION (why it is not infinite / not trivially-different):
  · the map/op VOCABULARY is finite (a curated tower list — could be interner-extracted).
  · GRADE is a PARAMETER: verify over a range, emit ONE ∀-quantified lemma (not one per grade).
  · a fact that is DEFINITIONAL (holds by the map's own recursion, e.g. decode-◂) or that
    is a CONSEQUENCE of another is flagged, not re-emitted.
  · (downstream) the interner dedups PROOF skeletons — trivially-different proofs collapse.

So the output is the finite set of DISTINCT parameterizable naturality lemmas.
"""
from itertools import product

# ---- Perm-level ops (numpy-free; plain lists — the Fin-vector model) ----
def punchin(p, x): return x if x < p else x + 1
def insert_at(p, s): return [p] + [punchin(p, v) for v in s]      # Perm n -> Perm (suc n)
def decode(digits):                                              # LehmerPath -> Perm
    s = []
    for d in digits: s = insert_at(d, s)
    return s
def blockSum(s, t): m = len(s); return list(s) + [m + v for v in t]   # ⊕ on Perm
def tensor(s, t):                                                # ⊗ on Perm (combine i j = i*n+j)
    n = len(t); out = [0] * (len(s) * n)
    for i in range(len(s)):
        for j in range(n): out[i * n + j] = s[i] * n + t[j]
    return out
def sign(s):                                                     # parity of inversions (0/1)
    inv = sum(1 for i in range(len(s)) for j in range(i + 1, len(s)) if s[i] > s[j])
    return inv & 1

# ---- LehmerPath-level ops (on digit lists; from the Agda recursions) ----
# _⊕_ :  start ⊕ l = l ;  (l₁ ◂ p) ⊕ l₂ = (l₁ ⊕ l₂) ◂ (inject+ p)   ⇒  l₁ ⊕ l₂ = l₂ ++ l₁ (values kept)
def lp_oplus(a, b): return list(b) + list(a)

def all_paths(n):                                                # every LehmerPath of grade n
    if n == 0: yield []; return
    for pre in all_paths(n - 1):
        for d in range(n): yield pre + [d]                       # p_{n-1} : Fin n

# ---- the enumerator ----
K = 5
# MAPS are LehmerPath -> X, each tagged with its codomain type (picks the target-op family).
MAPS = {
    "decode":      (lambda l: decode(l),        "perm"),
    "sign":        (lambda l: sign(decode(l)),  "bool"),
    "len":         (lambda l: sum(l),           "nat"),   # Σ Lehmer digits (Coxeter length)
}
SOURCE_OPS = {"⊕ˢ": lp_oplus}                             # (⊗ˢ needs the replay model — separate TODO)
# target-op families, keyed by the map's codomain — this is the TYPE-COMPATIBILITY prune.
TARGET_OPS = {
    "perm": {"blockSum": blockSum, "tensor": tensor},
    "bool": {"xor": lambda a, b: a ^ b, "and": lambda a, b: a & b},
    "nat":  {"+": lambda a, b: a + b, "*": lambda a, b: a * b},
}

def verify(F, op_s, op_t):
    """the naturality square:  F (op_s l1 l2) == op_t (F l1) (F l2)  over all paths, grades < K."""
    for m, n in product(range(K), range(K)):
        for l1, l2 in product(all_paths(m), all_paths(n)):
            if F(op_s(l1, l2)) != op_t(F(l1), F(l2)):
                return (m, n, l1, l2)
    return None

def main():
    print(f"enumerating naturality squares  F(op_s l1 l2) == op_t (F l1)(F l2)")
    print(f"  MAPS={list(MAPS)}  SOURCE={list(SOURCE_OPS)}  (grades < {K}; type-compatible targets only)\n")
    hold, fail = [], []
    for (fn, (F, cod)), (sn, op_s) in product(MAPS.items(), SOURCE_OPS.items()):
        for tn, op_t in TARGET_OPS[cod].items():          # ONLY codomain-compatible target ops
            cx = verify(F, op_s, op_t)
            tag = f"{fn}({sn} x y) = {tn}({fn} x)({fn} y)"
            (hold if cx is None else fail).append(tag)
            print(f"  {'✓ HOLDS ' if cx is None else '✗ fails '} {tag}"
                  + ("" if cx is None else f"   ✗grade {cx[0]},{cx[1]}"))
    print("\n  (·) decode(l ◂ p) = insert_at p (decode l)  — DEFINITIONAL (decode's own recursion), not re-emitted")
    print(f"\nfinite family: {len(hold)+len(fail)} type-compatible candidates → "
          f"{len(hold)} DISTINCT parameterizable naturality lemmas:")
    for h in hold: print("   →", h)

if __name__ == "__main__":
    main()
