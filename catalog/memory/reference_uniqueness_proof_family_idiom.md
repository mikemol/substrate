---
name: reference_uniqueness_proof_family_idiom
description: "The ∃!-universal-arrow uniqueness-proof FAMILY in substrate + the one compiling idiom (with two meta-gotchas). All *-unique lemmas share it; don't re-derive or re-search."
metadata: 
  node_type: memory
  type: reference
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

The substrate has a recurring FAMILY of **uniqueness-of-the-universal-map** proofs — the ∃! half of every universal property. They are ALL the same proof shape; before writing a new `*-unique`, reuse this idiom (don't re-dispatch a search — mapped 2026-06-26).

**Members (the ∃!-universal-arrow family):**
- `Algebra.Nat.GCD.Fold.eea-fold-unique` — `EEATrace` recursor (indexed initial algebra).
- `Category.UniversalProperty.Eval.foldUPTerm-unique` — `UPTerm` (indexed, 2-arc).
- `Category.FreeUniversalProperty.FreeMonoid.extend-unique` — `Word`/free monoid (Set-basis). The free-monoid FreeUP (`free-monoid : FreeUP monoid-class Gen (Word Gen)`) is BUILT here.
- `Category.FreeUniversalProperty.FreeF2Module.ext-unique` — free F₂-module (`Vector`).
- `Algebra.R.Trace.Final.ana-unique` — `RealTrace` terminal coalgebra (the COINDUCTIVE dual; uses guarded-corecursion + witness-threading, NOT cong — see below).
- GAPS (not built): `trace-fold-unique` (generic `Wedge.Trace`, the would-be common parent), `eea-fold-poly-unique` (`PolyEEATrace`).

**The INDUCTIVE idiom (two-constructor indexed family, e.g. base/step):**
```
foo-unique {T} … (base a)       = h-base a
foo-unique {T} … {a = a}{g = g} (step b w sub) =
  trans (h-step b w sub) (cong (interp {a}{g} b w) (foo-unique {T} … sub))
```
i.e. `trans (the step-commutes hyp) (cong (the step-interp) (recurse))`; base case = the base hyp.

**Two meta-gotchas that block compilation (both hit on eea-fold-unique):**
1. **Output-only indices must be bound explicitly.** If the step-interp's result index (e.g. `a` in `T a (suc b) g`) is NOT among its inputs, `cong (interp b w)` can't infer it → unsolved metas. Bind it on the LHS (`{a = a}{g = g}`) and pass `interp {a}{g} b w`. (Contrast `foldUPTerm-unique`'s `cmpT`, whose indices are all input-pinned, so it needs no binding.)
2. **Pass the family `{T}` explicitly to the fold in the conclusion.** `eea-fold {T} …` — because `base-interp : (a) → T a 0 a` has a LITERAL index (`0`), making `{T}` a higher-order non-pattern (uninferable). All the folds (`gcd-fold` etc.) pass `{T}` explicitly for this reason.

**The COINDUCTIVE dual idiom** (`ana-unique`): do NOT use `cong` (bisimilarity `~` is a coinductive record, and cong breaks guardedness). Thread a `t ≡ h s` witness into a helper `go`, consume it with `refl` at copattern time, put the corecursive call directly under the `~` constructor.

This family IS the universal-arrow ∃!-layer the groupoid-reification ([[project_open_threads]] Ⓤ.reify-interconnect) needs: every non-invertible interconnect edge factors through one of these. Sibling of [[free-universal-property]] (the apex). Per [[feedback_reuse_search_before_feasibility_conclusions]] / the widened CLAUDE.md: this memo IS the "already-named structure" to find instead of re-searching.
