---
name: fin-literals-arc
description: "Fin.Literals (₀ ... ₁₅) + fin×fin-cover migrations replacing hand-spelled `suc (suc ...)` chains and N×M refl-tables. The substrate's \"delegate to existing primitives\" instinct applied to Nat-index counting."
metadata: 
  node_type: memory
  type: project
  originSessionId: d49d2868-8ade-4add-9d72-b31958685ef0
---

The substrate has long had:
- `Substrate.Groups.Coxeter.CanonicalCover.n-refls / copies` — produce n-element tuples of a uniform value (parametric in n)
- `Substrate.Foundation.Fin.Cover.{fin-cover, fin×fin-cover, tabulate, dep-Pow}` — Cayley-table cover machinery

What was MISSING: a literal notation for small Fin values. Every position 2 in Fin 4 had to be written as `suc (suc zero)` (10 chars) and pattern-matched against `suc (suc zero)`. Every position 9 in Fin 10 took 48 characters of nested `suc`s.

**Commit a0c91dc** — `Substrate.Foundation.Fin.Literals` defines subscript-digit pattern synonyms ₀ … ₁₅, polymorphic in the implicit Fin size, usable in both expression AND pattern positions. Migrated 501 `(suc (suc … zero))` occurrences across 75 files. Worst offender: `Stab-S3-Extend.agda` (56 chains → 0).

**Commit d61a462** — Second pass with the user's "still a lot of suc (suc out there" pointer:
- Extended Fin.Literals to ₃₂ (was ₁₅) for higher-arity sites like `TokiPona/Nimi` (Fin indices up to ~30 for word vocabulary).
- Iteratively folded `suc (suc … ₍subscript-or-zero₎ …)` chains through the ladder — 652 more substitutions across 93 files. First pass missed these because the chain's BASE was already a subscript (e.g. `suc (suc ₁₀)` → `₁₂` ↔ first pass only handled `(suc (suc zero))` → `₂`).
- Migrated 15 Fin-N wildcard catch-alls of the form `f (suc (suc _)) = ...` (the "last case" pattern in a function over Fin n) to `f ₍n-1₎ = ...`.

After two passes: 110 → 18 remaining `suc (suc ` occurrences. The 18 remaining are all legitimate uses (see commit msg).

**Subtle gotcha encountered:** depth-to-subscript mapping was OFF BY ONE in the second-pass script's first attempt — `(suc (suc _))` has 2 sucs and represents value 2 (Fin n with n ≥ 3's third inhabitant), should be `₂`, not `₁`. The first version mapped `depth=2 → ₁` which broke `complement (suc (suc (suc (suc (suc _)))))` (5 sucs) to `₄` instead of `₅`. Fixed by recomputing the map as `depth k → ₍k₎`.

**Commit 897d6b3** — `is-symmetric-bridged-{3,4}` rewritten from 9-/16-row case tables to `fin×fin-cover + nested-refl tuple`:

```agda
is-symmetric-bridged-4 M =
  fin×fin-cover (λ i j → SymBilinForm-4-to-generic M i j
                       ≡ SymBilinForm-4-to-generic M j i)
    ( (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    ,  refl , refl , refl , refl )
```

16 lines → 7 lines. The refl-tuple structure mirrors the matrix's row-major layout; the deltas (arity, equation predicate) are visibly the only per-instance content.

**Methodology pointer:** when a function definition has a SHAPE that's just "exhaust Fin n × Fin m with refl per cell," look for an existing cover primitive in `Foundation.Fin.Cover` rather than typing it out by hand. The substrate's "delegate to existing primitives" instinct (per the c-pos migration lesson) usually pays off — Fin.Cover existed long before this arc; was just being underused.

**Caveat from Fin.Cover.tabulate's doc:** the uniform `tabulate _ (λ _ → refl)` form FAILS for heterogeneous-equation predicates (each cell's refl has a different type that Agda's higher-order unification can't promote from a single lambda body). For those, you write the nested-tuple of refls explicitly — Agda picks each refl's type at the leaf. This is the pattern used in `is-symmetric-bridged-{3,4}` (and which `tabulate` cannot replace).

See also: [[project_cpos_migration_arc]] (the precursor — same delegation methodology, applied to canonical-witness names), [[project_cluster_to_action_analysis_2026_05]] (the SPPF lens that identified this kind of pattern).
