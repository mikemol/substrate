#!/usr/bin/env python3
"""nat_enum.py — ⟡nat-enum: enumerate tower NATURALITY FACTS (homomorphism squares) by
numpy verification, then EMIT the verified-true ones as Agda lemma statements.

A naturality fact is a hom square   F (op_s x y) == op_t (F x) (F y).
`decode-⊕` / `decode-⊗ˢ` are two INSTANCES of one template ("decode is a monoidal hom").
This enumerates the family over a finite (map × op-pair) vocabulary, verifies each on all
finite instances up to grade K, and — the productionization over the prototype —

  · models ⊗ˢ (the factoradic replay), so decode-⊗ˢ is auto-found alongside decode-⊕;
  · CHECKS the tree (catalog/reuse-index.md + grep) so already-PROVEN facts are referenced,
    not re-emitted (the reuse discipline: don't regenerate what exists);
  · EMITS the NEW verified facts as an Agda candidate module (statement + `?`), the synthesis
    hand-off (proof is the LLM/by-hand step — honest scope, per the auto-pushout design).

TRUNCATION (finite, non-trivial): finite map/op vocab; codomain type-compat prunes the cross
product; grade is a ∀-PARAMETER (one lemma, not one-per-grade); definitional / already-proven
facts are filtered. Downstream: the interner dedups proof skeletons (the on-iso template).

Usage:
  python3 jea/metalanguage/nat_enum.py                 # enumerate + report (existing vs new)
  python3 jea/metalanguage/nat_enum.py --emit OUT.agda # + write the NEW facts as an Agda module
"""
from __future__ import annotations
import sys, os, argparse, subprocess
from itertools import product

# ------------------------------------------------------------------ Fin-vector models
def punchin(p, x): return x if x < p else x + 1
def insert_at(p, s): return [p] + [punchin(p, v) for v in s]
def decode(digits):
    s = []
    for d in digits: s = insert_at(d, s)
    return s
def blockSum(s, t): m = len(s); return list(s) + [m + v for v in t]        # Perm ⊕
def tensor(s, t):                                                          # Perm ⊗ (combine i j = i*n+j)
    n = len(t); out = [0] * (len(s) * n)
    for i in range(len(s)):
        for j in range(n): out[i * n + j] = s[i] * n + t[j]
    return out
def sign(s):
    return sum(1 for i in range(len(s)) for j in range(i + 1, len(s)) if s[i] > s[j]) & 1
def length(digits): return sum(digits)                                     # Σ Lehmer digits (Coxeter length)

# LehmerPath ops on digit lists (from the Agda recursions):
def lp_oplus(a, b): return list(b) + list(a)                               # _⊕_
def lp_otimes(a, b):                                                       # _⊗ˢ_ : offsetDigit p n q = p*n+q
    n = len(b); return [p * n + q for p in a for q in b]

def all_paths(n):
    if n == 0: yield []; return
    for pre in all_paths(n - 1):
        for d in range(n): yield pre + [d]

# ------------------------------------------------------------------ the vocabulary (numpy models + Agda qnames)
K = 5
# map name -> (F : LehmerPath->X, codomain tag, agda-application (X↦term, APPLIED form), import homes)
MAPS = {
    "decode": (lambda l: decode(l),       "perm", (lambda x: f"decode {x}"),
               ["Substrate.WitnessTower.LehmerPath"]),
    "sign":   (lambda l: sign(decode(l)), "bool", (lambda x: f"sign (decode {x})"),
               ["Substrate.WitnessTower.LehmerPath",
                "Substrate.WitnessTower.Wedge.OrientationRigCatPermSign"]),
    "len":    (lambda l: length(l),       "nat",  (lambda x: f"pyLength {x}"),
               ["Substrate.WitnessTower.Wedge.PyAstRewriteSemantics"]),
}
# source op name -> (op on digit lists, Agda qname)
SOURCE_OPS = {
    "⊕": (lp_oplus,  "Substrate.WitnessTower.Wedge.OrientationSum._⊕_"),
    "⊗ˢ": (lp_otimes, "Substrate.WitnessTower.Wedge.OrientationProductStructural._⊗ˢ_"),
}
# target op families keyed by codomain (the type-compatibility prune)
TARGET_OPS = {
    "perm": {"blockSum": (blockSum, "Substrate.WitnessTower.Wedge.OrientationDistributor.blockSum"),
             "_⊗_":      (tensor,   "Substrate.WitnessTower.Wedge.OrientationProduct._⊗_")},
    "bool": {"_xor_": ((lambda a, b: a ^ b), "Substrate.Foundation.Bool._xor_")},
    "nat":  {"_+_": ((lambda a, b: a + b), "Substrate.Foundation.Nat._+_"),
             "_*_": ((lambda a, b: a * b), "Substrate.Foundation.Nat._*_")},
}

def verify(F, op_s, op_t):
    for m, n in product(range(K), range(K)):
        for l1, l2 in product(all_paths(m), all_paths(n)):
            if F(op_s(l1, l2)) != op_t(F(l1), F(l2)):
                return (m, n)
    return None

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
def already_proven(fn, sn, tn):
    """grep the agda tree for an existing lemma of this shape (reuse: don't re-emit)."""
    pats = {("decode", "⊕", "blockSum"): "decode-⊕", ("decode", "⊗ˢ", "_⊗_"): "decode-⊗ˢ"}
    name = pats.get((fn, sn, tn))
    if not name: return None
    try:
        r = subprocess.run(["grep", "-rl", f"{name} :", os.path.join(REPO, "agda", "Substrate")],
                           capture_output=True, text=True, timeout=20)
        return name if r.stdout.strip() else None
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", help="write NEW verified facts to this Agda module path")
    args = ap.parse_args()

    print(f"⟡nat-enum: hom-square family over MAPS={list(MAPS)} × SOURCE={list(SOURCE_OPS)}  (grades < {K})\n")
    facts = []   # (fn, sn, tn, F_agda, op_s_qn, op_t_qn, cod, status)
    for (fn, (F, cod, fa, fhome)), (sn, (op_s, s_qn)) in product(MAPS.items(), SOURCE_OPS.items()):
        for tn, (op_t, t_qn) in TARGET_OPS[cod].items():
            cx = verify(F, op_s, op_t)
            if cx is not None:
                print(f"  ✗ {fn}({sn}) ≠ {tn}   (grade {cx[0]},{cx[1]})"); continue
            prov = already_proven(fn, sn, tn)
            status = f"PROVEN ({prov})" if prov else "NEW"
            facts.append((fn, sn, tn, fa, s_qn, t_qn, cod, status))
            print(f"  ✓ {fn}({sn} x y) = {tn}({fn} x)({fn} y)   [{status}]")

    new = [f for f in facts if f[7] == "NEW"]
    print(f"\n{len(facts)} verified naturality lemmas — {len(facts)-len(new)} already proven, {len(new)} NEW:")
    for f in new: print(f"   → {f[0]}({f[1]}) = {f[2]}")

    if args.emit and new:
        emit_agda(args.emit, new)
        print(f"\n[emit] wrote {len(new)} candidate lemma(s) → {args.emit}")

def emit_agda(path, new):
    mod = os.path.splitext(os.path.basename(path))[0]
    homes = {"Substrate.Foundation.Eq", "Substrate.WitnessTower.LehmerPath"}
    for (fn, sn, tn, fa, s_qn, t_qn, cod, _) in new:
        homes |= set(MAPS[fn][3])
        homes.add(s_qn.rsplit(".", 1)[0])
        homes.add(t_qn.rsplit(".", 1)[0])
    L = [f"-- ⟡nat-enum CANDIDATES — numpy-verified naturality facts, proofs pending (synthesis hand-off).",
         f"-- Each holds on ALL instances up to grade {K}; `?` is the by-hand/LLM proof step.",
         "{-# OPTIONS --without-K #-}", "",
         f"module {mod} where", ""]
    for h in sorted(homes): L.append(f"open import {h}")
    L.append("")
    for (fn, sn, tn, fa, s_qn, t_qn, cod, _) in new:
        sop = s_qn.rsplit(".", 1)[1]
        lhs = fa(f"({sop} l₁ l₂)")
        rhs = f"{tn} ({fa('l₁')}) ({fa('l₂')})"
        L.append(f"{fn}-{sn} : ∀ {{m n}} (l₁ : LehmerPath m) (l₂ : LehmerPath n) →")
        L.append(f"  {lhs} ≡ {rhs}")
        L.append(f"{fn}-{sn} l₁ l₂ = ?")
        L.append("")
    with open(path, "w") as fh: fh.write("\n".join(L))

if __name__ == "__main__":
    main()
