#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""respell_typealias.py — ⟡set1-respell-typealias: table-driven respell of alias-headed type signatures.

A def `X : Fam A` is census-counted at level 1 SOLELY because the elaborated core keeps the alias head
(`Fam A : Set₁`) un-normalized; the definitionally-equal `X : A → Set` peels to codomain-Sort Set → level 0
(empirically probe-verified). This applies the saturation agent's EXACT (file, old, new) table — qname-safe
by construction (every edit is a full-line literal; the UniquenessStencilAbstract local `Rel` and all
binder/domain positions are simply not in the table). Aliases themselves are KEPT (binders still use them).

Exact payoff (agent-verified against the census): −33 = Fam 21 + Rel 10 + P 1 + Sub 1.
Map excluded (Σ-holder, irreducible). DRY RUN by default; --apply writes.
"""
import sys, difflib

A = "agda/Substrate/"
EDITS = [
    # ── Fam: 17 top-level sigs ──
    (A+"Category/Allegory/Refinement.agda",
     "iterate : {A : Set} → Refinement A → ℕ → Fam A → Fam A",
     "iterate : {A : Set} → Refinement A → ℕ → (A → Set) → A → Set"),
    (A+"Category/UniversalProperty/ExtrudeCoEmitGraded.agda",
     "R⁰ : Fam ℕ",
     "R⁰ : ℕ → Set"),
    (A+"Category/UniversalProperty/ExtrudeCoEmitGraded.agda",
     "Φ-obs : Fam ℕ → Fam ℕ",
     "Φ-obs : (ℕ → Set) → ℕ → Set"),
    (A+"Category/UniversalProperty/ExtrudeCoEmitGraded.agda",
     "Φ-pair-exact : RFam RTPair → RFam RTPair",
     "Φ-pair-exact : (RTPair → Set) → RTPair → Set"),
    (A+"Category/UniversalProperty/ExtrudeCoEmitGraded.agda",
     "P⁰-pair : RFam RTPair",
     "P⁰-pair : RTPair → Set"),
    (A+"Algebra/Wedge/TraceKleeneColimit.agda",
     "⊥-fam : Fam (Idx D)",
     "⊥-fam : Idx D → Set"),
    (A+"Algebra/Wedge/TraceKleeneColimit.agda",
     "Colim : Fam (Idx D)",
     "Colim : Idx D → Set"),
    (A+"Algebra/Wedge/TraceMuStep.agda",
     "Φ-step : Fam Idx → Fam Idx",
     "Φ-step : (Idx → Set) → Idx → Set"),
    (A+"Algebra/Wedge/TraceMuStep.agda",
     "TraceF : Fam Idx",
     "TraceF : Idx → Set"),
    (A+"Algebra/Wedge/TraceNuColimit.agda",
     "⊤-fam : Fam (Idx D)",
     "⊤-fam : Idx D → Set"),
    (A+"Algebra/Wedge/TraceNuColimit.agda",
     "Limit : Fam (Idx D)",
     "Limit : Idx D → Set"),
    (A+"Algebra/Wedge/TraceNuConstructive.agda",
     "ν-carrier    : Fam (Idx D)",
     "ν-carrier    : Idx D → Set"),
    (A+"Algebra/Wedge/CertifiedPhiStep.agda",
     "Φ-cert : Fam Idxℕ → Fam Idxℕ",
     "Φ-cert : (Idxℕ → Set) → Idxℕ → Set"),
    (A+"Algebra/Wedge/CertifiedPhiStep.agda",
     "⊤-cert : Fam Idxℕ",
     "⊤-cert : Idxℕ → Set"),
    (A+"Algebra/Wedge/CertifiedPhiStep.agda",
     "Limit-cert : Fam Idxℕ",
     "Limit-cert : Idxℕ → Set"),
    (A+"Algebra/R/Trace/SKIGradedFlatAllegory.agda",
     "R⁰ : Fam ℕ",
     "R⁰ : ℕ → Set"),
    (A+"Algebra/R/Trace/SKIGradedFlatAllegory.agda",
     "Φ-arity : Fam ℕ → Fam ℕ",
     "Φ-arity : (ℕ → Set) → ℕ → Set"),
    # ── Fam: 4 FIELD types (their projection defs are census-counted) ──
    (A+"Category/Allegory/Refinement.agda",
     "Φ    : Fam A → Fam A",
     "Φ    : (A → Set) → A → Set"),
    (A+"Category/UniversalProperty/FixpointStencilRecord.agda",
     "μ-A μ-B      : Fam (Idx D)",
     "μ-A μ-B      : Idx D → Set"),
    (A+"Category/UniversalProperty/FixpointStencilRecord.agda",
     "ν-carrier    : Fam (Idx D)",
     "ν-carrier    : Idx D → Set"),
    # ── Rel: 10 codomain respells ──
    (A+"Category/Allegory.agda",
     "idR : (A : Set) → Rel A A",
     "idR : (A : Set) → A → A → Set"),
    (A+"Category/Allegory.agda",
     "_⨾_ : {A B C : Set} → Rel A B → Rel B C → Rel A C",
     "_⨾_ : {A B C : Set} → Rel A B → Rel B C → A → C → Set"),
    (A+"Category/Allegory.agda",
     "_† : {A B : Set} → Rel A B → Rel B A",
     "_† : {A B : Set} → Rel A B → B → A → Set"),
    (A+"Category/Allegory.agda",
     "_∧_ : {A B : Set} → Rel A B → Rel A B → Rel A B",
     "_∧_ : {A B : Set} → Rel A B → Rel A B → A → B → Set"),
    (A+"Category/Allegory/Division.agda",
     "_∖_ : {A B C : Set} → Rel A B → Rel A C → Rel B C",
     "_∖_ : {A B C : Set} → Rel A B → Rel A C → B → C → Set"),
    (A+"Category/Allegory/Division.agda",
     "_／_ : {A B C : Set} → Rel B C → Rel A C → Rel A B",
     "_／_ : {A B C : Set} → Rel B C → Rel A C → A → B → Set"),
    (A+"Category/Allegory/Maps.agda",
     "graph : {A B : Set} → (A → B) → Rel A B",
     "graph : {A B : Set} → (A → B) → A → B → Set"),
    (A+"Category/Allegory/Refinement.agda",
     "BWedge : ℕ → Rel ℕ (ℕ × ℕ)",
     "BWedge : ℕ → ℕ → ℕ × ℕ → Set"),
    (A+"Category/Allegory/Power.agda",
     "unname : {A B : Set} → (A → P B) → Rel A B",
     "unname : {A B : Set} → (A → P B) → A → B → Set"),
    (A+"Category/UniversalProperty/StencilModularMap.agda",
     "cross-graph : Rel (A × B) R",
     "cross-graph : A × B → R → Set"),
    # ── P: 1 (codomain P B = B → Set; A → P B = A → B → Set) ──
    (A+"Category/Allegory/Power.agda",
     "name : {A B : Set} → Rel A B → (A → P B)",
     "name : {A B : Set} → Rel A B → A → B → Set"),
    # ── Sub: 1 ──
    (A+"Category/UniversalProperty/DiagonalPolishDerivative.agda",
     "D : Sub → Sub",
     "D : Sub → Point → Set"),
]

byfile = {}
for f, old, new in EDITS:
    byfile.setdefault(f, []).append((old, new))

# ⚑ ONE ACT: state the intent AND snapshot, BEFORE `APPLY` is bound.  The `guard`
# this supersedes sat under `if APPLY:` in the write loop — reached only once APPLY
# was already TRUE, so the UNSTATED case never reached it.
# ⚑ `paths=` IS THE WHOLE TARGET SET, which this tool uniquely CAN name in full:
# `EDITS` is a literal table, so the population is known before any read. The
# per-file `guard` armed on the first file and no-oped after, so `_copy_untracked`
# only ever saw one of them.
import os as _o3
sys.path.insert(0, _o3.path.dirname(_o3.path.abspath(__file__)))
import edit_snapshot as _es
_es.require_at_entry("respell_typealias", paths=sorted(byfile))
APPLY = "--apply" in sys.argv

fail = 0
for f, subs in byfile.items():
    src = open(f).read()
    out = src
    for old, new in subs:
        n = out.count(old)
        if n != 1:
            print(f"✗ {f}: expected exactly 1 occurrence of {old!r}, found {n}")
            fail = 1
            continue
        out = out.replace(old, new)
    if out == src:
        continue
    if APPLY:
        # ⚑ recoverable-by-construction: this rewrites a file it read.
        import edit_snapshot as _es; _es.guard("respell_typealias", [f])
        open(f, "w").write(out)
        print(f"# APPLIED {f} ({len(subs)} respells)")
    else:
        sys.stdout.writelines(difflib.unified_diff(
            src.splitlines(True), out.splitlines(True), fromfile=f, tofile="(respelled)"))
sys.exit(fail)
