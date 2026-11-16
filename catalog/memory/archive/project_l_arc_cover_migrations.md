---
name: project-l-arc-cover-migrations
description: "L-arc landings of the three-layer cover combinator framework: V4/Operations now hosts v4-cover / v4×v4-cover / v4×v4×v4-cover; Axes re-exports them; V4.Axioms 112→30 lines; Stab-S3 + Twist + HomRotations + HomSwaps + Duality + Z4-Coxeter all migrated. See [[feedback-expose-generator-not-orbit-applies]] for the framework."
metadata: 
  node_type: memory
  type: project
  originSessionId: 20608575-0873-42b7-b664-8addeb8207d9
---

The L-arc executes the three-layer cover framework from
[[feedback-expose-generator-not-orbit-applies]] across the substrate's
remaining Cayley-table enumerations. ~200 lines of refl-block
enumeration collapsed across 10 modules.

**Where the V₄/Axis cover primitives now live:**
* `Substrate.Groups.V4.Operations` — `v4-cover`, `v4×v4-cover`,
  `v4×v4×v4-cover` (4-cube for ·-assoc). Sourced HERE because V4.Axioms
  imports V4.Operations directly (no dependency-cycle risk to Axes).
* `Substrate.Axes` — `axis-cover`, `axis×axis-cover` (Axis-specific);
  re-exports the V₄ covers `public` from V4.Operations so downstream
  callers can `open import Substrate.Axes using (v4×v4-cover)` etc.
* `Substrate.Groups.Z{2,3,4}-Coxeter` — `canonical-cover-Z{n}` for the
  per-instance Canonical types.

**Why:** decomposition of finite Cayley tables into a single-axis cover
combinator + tuple payload exposes the generator (constructor
enumeration) once per type and reuses it via tensor composition for
N×M / N×M×K tables. Atlas-of-charts decomposition applied to
constructor enumerations.

**How to apply:** when writing a new function over a finite-constructor
type with ≥6 cases (or ≥4 with a clean refl-uniform payload), use the
type's cover combinator. For 2-axis Cayley tables, use the product
cover (v4×v4-cover, axis×axis-cover) rather than enumerating all N·M
cells. For deeply nested patterns (3+ axes), supply an explicit
predicate lambda — Agda's higher-order unification can't infer
`_` through multiple cover layers (failure mode observed: 
`UnsolvedConstraints _P_N` blocked).

**Landings (this arc):**
* `Substrate.Groups.V4.Axioms` — 112→30 lines. ε-left/right, inv-left/
  right (4-case each), ·-assoc (64-case via v4×v4×v4-cover),
  ·-comm (16-case via v4×v4-cover), ·-right-cancel-ε (16-case mixed
  refl + λ() via v4×v4-cover).
* `Substrate.Cardinality` — 5 bijection round-trips via fin-cover.
* `Substrate.Axes` — axis-of-v-v-of-axis, v-of-axis-axis-of-v.
* `Substrate.Groups.Stab-S3` — fin3-non-anchor-fin3 (12-case),
  non-anchor-fin3-non-anchor (16-case mixed), fin3-to-non-anchor-≢
  (12-case absurd).
* `Substrate.Groups.Stab-S3-Hom` — extend-hom-ε (16-case Axis×Axis).
* `Substrate.Groups.Actions.S3-on-V4.{Twist, HomRotations, HomSwaps}` —
  swap-rotate-twist (4→1), rot-pow-swap-twist (12→3), act-equals-pow
  (24→6), hom-rot / hom-rot² / hom-swap-αβ / hom-swap-αγ / hom-swap-βγ
  (16→6 each).
* `Substrate.ShadowArchitecture.Duality` — normal-dual-line and
  dual-line-normal (7-Point and 7-Line round-trips) via local
  point-cover / line-cover.
* `Substrate.Groups.Z4-Coxeter` — 6 functions × 4 cases each, via
  newly-added canonical-cover-Z4 (with explicit predicate lambdas).

**Failure-mode observed (the rule that earned its own line):** the
nested `cover _ (cover _ (cover _ ...))` pattern with implicit
predicates fails when there are 3+ layers — Agda can't propagate the
result-type from the innermost upward. Workaround: either (a) supply
explicit `λ {x} _ → ...` predicates at the inner layers, or (b) split
the top axis off via per-constructor pattern matching and apply the
product cover only to the inner two axes (e.g. act-equals-pow's 6 cases
of (Z₃-canonical × Z₂-canonical) × v4-cover).

**Anti-pattern flagged (and not pursued):** migrations where the cover
form replaces N lines with N lines of explicit-predicate-lambda + tuple.
The win threshold is "≥6 cases" or "Agda can infer predicate from `_`."
Below that, the per-case enumeration is more readable. Recorded as
[[feedback-expose-generator-not-orbit-applies]] Layer 2 corollary.
