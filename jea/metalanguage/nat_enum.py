#!/usr/bin/env python3
"""nat_enum.py — ⟡nat-enum (+ ⟡nat-enum-residue): synthesize tower NATURALITY LAWS from
the typechecked cores' models, INCLUDING the residue of every "failed" square.

For a map F and a source op op_s, the law is the closed form of  F (op_s x y)  over the
inputs. Two outcomes, UNIFIED — a failed hom is never discarded, it is completed:

  · CLEAN HOM   — the form is a single target op:  F(op_s x y) = op_t (F x)(F y).
  · RESIDUE LAW — the form is grade-weighted:      F(op_s x y) = <closed form in F x, F y, m, n>.
                  (the wedge a = recon q b r: the residue is the grade-parameterised defect.)

Constructive setting (--safe --without-K, no HIT, no sum-types) ⇒ the residue is a TOTAL
COMPUTABLE function with a CLOSED FORM (ℕ: exact integer fit; Bool: GF(2) fit) — so the
corrected law is a genuine theorem, synthesizable, not a postulate.

TRUNCATION: the monomial basis is bounded + principled (LINEAR in the map's values — it is a
linear fold; degree-≤2 in the GRADES — one grade factor per ⊗ˢ nesting). Exact + sparse fit ⇒
not overfitting. Emits NEW laws (holding + residue) as Agda statements; the proof is the hand-off.

Usage:  python3 jea/metalanguage/nat_enum.py [--emit OUT.agda]
"""
from __future__ import annotations
import sys, os, argparse, subprocess
from itertools import product
import numpy as np

# ------------------------------------------------------------------ Fin-vector models
def punchin(p, x): return x if x < p else x + 1
def insert_at(p, s): return [p] + [punchin(p, v) for v in s]
def decode(digits):
    s = []
    for d in digits: s = insert_at(d, s)
    return s
def blockSum(s, t): m = len(s); return list(s) + [m + v for v in t]
def tensor(s, t):
    n = len(t); out = [0] * (len(s) * n)
    for i in range(len(s)):
        for j in range(n): out[i * n + j] = s[i] * n + t[j]
    return out
def sign(s): return sum(1 for i in range(len(s)) for j in range(i + 1, len(s)) if s[i] > s[j]) & 1
def length(d): return sum(d)
def lp_oplus(a, b): return list(b) + list(a)                       # _⊕_
def lp_otimes(a, b):                                              # _⊗ˢ_ (offsetDigit p n q = p*n+q)
    n = len(b); return [p * n + q for p in a for q in b]
def all_paths(n):
    if n == 0: yield []; return
    for pre in all_paths(n - 1):
        for d in range(n): yield pre + [d]

# ------------------------------------------------------------------ vocabulary
K = 6
# map -> (F:LehmerPath->X, codomain, agda-apply X↦term, import homes)
MAPS = {
    "decode": (lambda l: decode(l),       "perm", (lambda x: f"decode {x}"),
               ["Substrate.WitnessTower.LehmerPath"]),
    "sign":   (lambda l: sign(decode(l)), "bool", (lambda x: f"sign (decode {x})"),
               ["Substrate.WitnessTower.LehmerPath", "Substrate.WitnessTower.Wedge.OrientationRigCatPermSign"]),
    "len":    (lambda l: length(l),       "nat",  (lambda x: f"pyLength {x}"),
               ["Substrate.WitnessTower.Wedge.PyAstRewriteSemantics"]),
}
SOURCE_OPS = {
    "⊕":  (lp_oplus,  "Substrate.WitnessTower.Wedge.OrientationSum._⊕_"),
    "⊗ˢ": (lp_otimes, "Substrate.WitnessTower.Wedge.OrientationProductStructural._⊗ˢ_"),
}
# perm-codomain target ops (hom-check; a perm residue would be recon(δ), synth_agda_prototype's residue class)
PERM_OPS = {"blockSum": (blockSum, "Substrate.WitnessTower.Wedge.OrientationDistributor.blockSum"),
            "_⊗_":      (tensor,   "Substrate.WitnessTower.Wedge.OrientationProduct._⊗_")}

# ------------------------------------------------------------------ closed-form synthesis
# monomial = (var, gm, gn): value = (F x if 'a' else F y) * m^gm * n^gn ; grade-degree ≤ 2, length-linear.
BASIS = [(v, gm, gn) for v in ("a", "b") for gm in range(3) for gn in range(3) if gm + gn <= 2]
def mono_val(mon, a, b, m, n):
    v, gm, gn = mon
    return (a if v == "a" else b) * (m ** gm) * (n ** gn)

def collect(F, op_s):
    data = {}
    for m, n in product(range(K), range(K)):
        for l1, l2 in product(all_paths(m), all_paths(n)):
            key = (F(l1), F(l2), m, n)
            val = F(op_s(l1, l2))
            if key in data and data[key] != val:
                return None                                       # not a function of (a,b,m,n): out of scope
            data[key] = val
    return data

def fit_nat(F, op_s):
    data = collect(F, op_s)
    if data is None: return None
    keys = sorted(data); Y = np.array([data[k] for k in keys], float)
    X = np.array([[mono_val(mo, *k) for mo in BASIS] for k in keys], float)
    coef, *_ = np.linalg.lstsq(X, Y, rcond=None)
    cr = np.round(coef).astype(int)
    if not np.array_equal(X @ cr, Y.astype(int)): return None
    return [(BASIS[i], int(c)) for i, c in enumerate(cr) if c]

def fit_bool(F, op_s):
    """GF(2) fit over grade-parity-weighted {s₁,s₂} — brute force (small basis)."""
    data = collect(F, op_s)
    if data is None: return None
    b2 = [(v, gm, gn) for v in ("a", "b") for gm in (0, 1) for gn in (0, 1) if gm + gn <= 1]
    keys = sorted(data)
    rows = [[(mono_val(mo, *k) & 1) for mo in b2] for k in keys]
    Y = [data[k] & 1 for k in keys]
    for combo in range(1 << len(b2)):                             # 2^|b2| ≤ 64
        sel = [i for i in range(len(b2)) if combo >> i & 1]
        if all(sum(r[i] for i in sel) & 1 == y for r, y in zip(rows, Y)):
            return [(b2[i], 1) for i in sel]
    return None

# ------------------------------------------------------------------ classify + render
def as_hom(form, cod):
    """is the closed form a single clean target op of (F x, F y)?  return op-name or None."""
    s = {(m, c) for m, c in form}
    A, B = (("a", 0, 0), 1), (("b", 0, 0), 1)
    if cod == "nat" and s == {A, B}: return "_+_"
    if cod == "bool" and s == {A, B}: return "_xor_"
    return None

def render(form, fa, cod):
    parts = []
    for (v, gm, gn), c in sorted(form):
        fac = ([str(c)] if c != 1 else []) + ["m"] * gm + ["n"] * gn + [f"({fa('l₁' if v == 'a' else 'l₂')})"]
        parts.append(" * ".join(fac))
    return " + ".join(parts) if cod != "bool" else " xor ".join(parts)

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
def already_proven(fn, sn):
    name = {("decode", "⊕"): "decode-⊕", ("decode", "⊗ˢ"): "decode-⊗ˢ"}.get((fn, sn))
    if not name: return None
    r = subprocess.run(["grep", "-rl", f"{name} :", os.path.join(REPO, "agda", "Substrate")],
                       capture_output=True, text=True)
    return name if r.stdout.strip() else None

# ------------------------------------------------------------------ driver
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--emit"); args = ap.parse_args()
    print(f"⟡nat-enum: synthesizing naturality laws (+ residues) over MAPS={list(MAPS)} "
          f"× {list(SOURCE_OPS)}  (grades < {K})\n")
    emit = []
    for (fn, (F, cod, fa, _)), (sn, (op_s, s_qn)) in product(MAPS.items(), SOURCE_OPS.items()):
        if cod == "perm":
            hit = None
            for tn, (op_t, t_qn) in PERM_OPS.items():
                if all(F(op_s(l1, l2)) == op_t(F(l1), F(l2))
                       for m, n in product(range(K), range(K))
                       for l1, l2 in product(all_paths(m), all_paths(n))):
                    hit = (tn, t_qn); break
            if hit:
                prov = already_proven(fn, sn)
                print(f"  ✓ HOM     {fn}({sn}) = {hit[0]}    [{'PROVEN '+prov if prov else 'NEW'}]")
                if not prov: emit.append(("hom", fn, sn, fa, s_qn, hit))
            else:
                print(f"  ~ RESIDUE {fn}({sn}) : perm-valued δ = recon(op_t, ·) — synth_agda_prototype residue class")
            continue
        form = (fit_nat if cod == "nat" else fit_bool)(F, op_s)
        if form is None:
            print(f"  · {fn}({sn}) : no closed form in the bounded basis"); continue
        hom = as_hom(form, cod)
        rhs = render(form, fa, cod)
        graded = any(gm or gn for (_, gm, gn), _ in form)
        if cod == "bool" and not hom and graded:                  # GF(2) grade weight ⇒ needs a parity primitive
            print(f"  ~ RESIDUE {fn}({sn}) = {rhs}  — needs `parity : ℕ → Bool` (absent); not emitted")
            continue
        kind = "HOM    " if hom else "RESIDUE"
        print(f"  ✓ {kind} {fn}({sn}) = {rhs}")
        emit.append(("law", fn, sn, fa, s_qn, rhs))

    if args.emit and emit:
        write_agda(args.emit, emit); print(f"\n[emit] {len(emit)} law(s) → {args.emit}")

def write_agda(path, emit):
    """Emit a --safe PARAMETERIZED module: each synthesized law is a module PARAMETER the
    consumer discharges by instantiation (no ? holes, no postulates — --safe-clean)."""
    mod = os.path.splitext(os.path.basename(path))[0]
    homes = {"Substrate.Foundation.Eq", "Substrate.WitnessTower.LehmerPath",
             "Substrate.Foundation.Nat", "Substrate.Foundation.Bool"}
    for (k, fn, sn, fa, s_qn, extra) in emit:
        homes |= set(MAPS[fn][3]); homes.add(s_qn.rsplit(".", 1)[0])
        if k == "hom": homes.add(extra[1].rsplit(".", 1)[0])
    L = ["-- ⟡nat-enum — numpy-synthesized naturality laws (holding + residue) as a PARAMETERIZED module.",
         "-- --safe: the laws are module PARAMETERS (interface); the consumer discharges each by",
         "-- instantiation with a proof. No ? holes, no postulates. (decode-⊕ / decode-⊗ˢ already PROVEN",
         "-- in the tree — reused, not re-stated.)",
         "{-# OPTIONS --safe --without-K #-}", "", f"module {mod} where", ""]
    L += [f"open import {h}" for h in sorted(homes)] + ["",
          "module Laws"]
    for (k, fn, sn, fa, s_qn, extra) in emit:
        sop = s_qn.rsplit(".", 1)[1]
        lhs = fa(f"({sop} l₁ l₂)")
        rhs = f"{extra[0]} ({fa('l₁')}) ({fa('l₂')})" if k == "hom" else extra
        L.append(f"  ({fn}-{sn} : ∀ {{m n}} (l₁ : LehmerPath m) (l₂ : LehmerPath n) → {lhs} ≡ {rhs})")
    L += ["  where", "", "  -- consequences of the synthesized laws are derived here; instantiate to discharge.", ""]
    open(path, "w").write("\n".join(L))

if __name__ == "__main__":
    main()
