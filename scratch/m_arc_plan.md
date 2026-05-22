# Algebraic-Structure Ladder arc (M-arc) — 10-slice plan

Foundational tower making ℚ-ring-laws (and the cascade) DERIVE
from a single typeclass instance rather than being patched per-arc.
Closes ~5 of the 9-10 substrate gaps identified in the audit
through structural unification; the others (Module-over-Ring,
Setoid/Equivalence, Conway-game-specific) need sibling towers
that this ladder enables but doesn't itself supply.

## Why this arc

Per the user's framing: "the visible surface should invariably be a
derivation of the layer underneath — surface-tension /
energy-minimization minimal-surface problem." Currently each gap
is a per-instance patch:
- ℚ-ring-laws sit as scattered TBD comments inside Q-arc
- ℚ-vector +-identity-laws are NOT proven (TPQ inherits the gap)
- RuleAction operad assoc/identity laws are stated as types only
- modify-Q-prod bilinearity is "deferred per coalgebraic discipline"

ALL of these dissolve if `ℚ` is a `Field` instance and `Field`
extends `Ring` which extends ... down to `Magma`. The visible
surface (ℚ-ring-laws) becomes a derivation of the layer underneath
(`Ring.+-comm`, `Ring.+-assoc`, etc.).

Per [[feedback-categorical-name-first]]: the standard algebra
ladder is the categorical name; substrate adopts it.

Per [[feedback-v4-typeclass-architecture]] applied at the algebra
layer (not group layer): V₄ inherits from Coxeter without
re-proving group laws. THIS arc extends that discipline downward
to the algebraic primitives.

## Gap-closure mapping

| Gap                                  | Closed at slice | How                                  |
|--------------------------------------|-----------------|--------------------------------------|
| ℚ-ring-laws (deferred in Q-arc)      | M10             | ℚ-Field instance → field accessors   |
| ℚ-vector +-identity laws (TPQ)       | M10 + M5        | ℚ-as-AbGroup → vector inherits       |
| ℚ-bilinearity (modify-Q-prod)        | M10 + M7        | Ring distributivity at ℚ             |
| RuleAction operad assoc + identity   | M3              | Monoid laws inherited                |
| GeneratorOperad right-identity       | M3              | Monoid right-identity                |
| F₁ as base case (not formalised)     | M3 (instance)   | Trivial Monoid `{*}`                 |
| ℚ-linear-extensionality (FLQ7/TPQ7)  | NOT YET         | Needs Module-over-Ring tower (next)  |
| B-arc IsNatural respect-≈M           | NOT YET         | Needs Setoid tower (separate)        |
| Conway addition general + transitivity | NOT YET       | Needs game-induction tower (separate)|

## Costructure shadows

- **`Magma`** — the universal generator (Carrier + _·_)
- **The "extends-with-one-law" pattern** — each level adds exactly
  one operation or law to its parent
- **Field-instance carriers** (F₁, F₂, ℚ) — leaf instances pulling
  laws via forgetful chain

## Ten slices

Annealing discipline ([[project-annealing-methodology]]).
Per [[feedback-minimize-stdlib-deps]]-strengthened: substrate-
native records; no stdlib Data.Group / Data.Field heavy machinery.
Per [[feedback-file-size-one-pass-rewrite]]: one Write per file.

### Phase 1 — Magma-Group ladder (M1-M5)

- **M1 `Substrate.Algebra.Magma`** — `record Magma (A : Set) : Set
  where field _·_ : A → A → A`. The universal generator. Includes
  the trivial-Magma instance (1-element) as a smoke test.

- **M2 `Substrate.Algebra.Semigroup`** — `record Semigroup (A : Set)
  : Set where field magma : Magma A; assoc : (a b c : A) → ...`. The
  "extends" pattern: contains a Magma + the new associativity law.

- **M3 `Substrate.Algebra.Monoid`** — Semigroup + identity element
  + two identity laws. **Includes F₁ as the trivial monoid `{*}`**
  (one element, * · * = *, identity *). Demonstrates the ladder
  accommodates the F₁ degenerate case naturally.

- **M4 `Substrate.Algebra.Group`** — Monoid + inverse function +
  inverse laws.

- **M5 `Substrate.Algebra.AbelianGroup`** — Group + commutativity.

### Phase 2 — Ring-Field ladder (M6-M8)

- **M6 `Substrate.Algebra.Semiring`** — Two Monoids (additive
  CommMonoid, multiplicative Monoid) + distributivity + zero-
  absorbs-multiplication.

- **M7 `Substrate.Algebra.Ring`** — Semiring with additive
  AbelianGroup (i.e., negation supplied). The standard Ring record.

- **M8 `Substrate.Algebra.Field`** — Ring + multiplicative inverse
  for nonzero + the inverse law. The leaf of the tower.

### Phase 3 — Instances + capstone (M9-M10)

- **M9 `Substrate.Algebra.F2.AsField`** — package F₂ as a Field
  instance using the existing `Substrate.Algebra.F2` infrastructure
  + `Substrate.Algebra.F2-CommutativeMonoid`. All F₂-ring-laws
  become Field-accessor projections. F₂ as a Field instance
  retroactively unifies the entire F₂ ecosystem with the new
  tower.

- **M10 `Substrate.Algebra.Q.AsField`** — package ℚ as a Field
  instance using `Substrate.Algebra.Z` + `Substrate.Algebra.Q.*`.
  **Closes the ℚ-ring-laws gap**: ring-+-comm, ring-+-assoc,
  ring-distrib, etc. become field-accessors. Demonstrates the
  cascade: Q-arc's deferred laws are now FIELD INSTANCE FIELDS.
  Plus capstone: re-export + summary + connection to the planned
  Module-over-Ring sibling tower.

## Substrate primitives engaged

- Substrate.Algebra.F2 + Substrate.Algebra.F2-CommutativeMonoid
- Substrate.Algebra.Z + Substrate.Algebra.Q.{Vector,Linear,Arithmetic,Order}
- The Coxeter framework (referenced for the inheritance discipline)

## Success criteria

1. All ten M-arc slices typecheck under `--safe --without-K`.
2. F₁ instantiates as `Substrate.Algebra.Magma`'s trivial instance
   (or M3's trivial Monoid), demonstrating the ladder's lower-
   degenerate behaviour.
3. F₂ instantiates as Field; all F₂-ring-laws become accessors.
4. ℚ instantiates as Field; the deferred Q-arc ring-laws become
   accessors (no new per-ℚ proofs needed beyond the Field instance
   data).
5. M10 demonstrates ≥3 currently-deferred ℚ-laws becoming field-
   accessor projections (worked examples).

## Deferred to sibling towers (NOT this arc)

- **Module-over-Ring tower** (~10 slices): closes ℚ-linear-
  extensionality, ℚ-vector arithmetic, FreeLinearizationR full
  builder. Depends on this arc's Ring (M7).
- **Setoid / Equivalence tower** (~5 slices): closes B-arc
  IsNatural-respect-≈M and similar. Independent of Ring tower.
- **Conway-game tower** (~10 slices): closes Conway addition +
  transitivity. Independent of Ring tower (uses surreal-specific
  birthday induction).
- **F₁-modules-as-pointed-sets** (~5 slices): the deeper F₁
  semantics where GL(n, F₁) = S_n, F₁-modules = pointed sets, etc.
  This arc only includes F₁ as the trivial-Monoid base case.

## Surface-tension framing

The deferred gaps form a SURFACE under tension: each per-instance
proof obligation is a local stretching. The minimal surface is the
unified tower where the visible surface (per-instance laws) is
EXACTLY the derivation of the tower's layer-by-layer extension
beneath. After M-arc:

- ℚ-ring-laws are NOT separate proofs but Field-instance fields
- F₂ inherits its existing laws via Field-instance fields too
- F₁ inhabits the base of the tower without further effort
- The next two sibling towers (Module-over-Ring, Setoid) can
  reference Ring (M7) without re-proving its content

The arc is foundational COSTRUCTURE that future arcs derive their
visible surface from.
