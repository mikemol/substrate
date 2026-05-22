# Quotient-as-UP arc plan (QU-arc)

Land "quotient algebra as a universal property" in the UP-topos so
that CRT and EEA become *instances* rather than ad-hoc artefacts.

## Why this organisation

The substrate already contains the moving parts of quotient algebra
several times over (see [[homology-cohomology-recursion]] —
catalogued patterns lifted to internal structure):

- [Substrate.Algebra.Q](agda/Substrate/Algebra/Q.agda) — ℤ × ℕ⁺ / cross-mult
- [Substrate.Conway.Equivalence](agda/Substrate/Conway/Equivalence.agda) — games / ≈ⁿ
- [Substrate.Groups.V4-Cosets](agda/Substrate/Groups/V4-Cosets.agda) — S₄ / V₄
- [Substrate.Groups.Coxeter.Word](agda/Substrate/Groups/Coxeter/Word.agda) — Word / normalize-equiv
- [Substrate.Algebra.Nat.GCD](agda/Substrate/Algebra/Nat/GCD.agda) + [Bezout](agda/Substrate/Algebra/Nat/Bezout.agda) — already has EEATrace; CRT is the missing structural lift
- [Substrate.Category.AbelianPFG](agda/Substrate/Category/AbelianPFG.agda) — names CRT for finite-abelian; structural lift missing

Each is a hand-built instance of the same UP. Naming the UP collapses
the pattern into a single primitive that every existing instance
inherits factorisation, uniqueness, and closure from — and CRT / EEA
fall out as morphism / composition facts in the UP-arrow category.

## Discipline

- Substrate-native: NO stdlib imports per [[feedback-minimize-stdlib-deps]] strengthened (2026-05-21).
  Use `Substrate.Foundation.{Eq, Product, ...}` already in tree.
- Canonical-rep encoding per [[project-agda-cubical-extraction-discipline]];
  no HITs. The quotient set is the image of a canonical-form
  function, not a HIT'd set-of-classes.
- USE the equivalence per [[feedback-use-vs-commit]] — do NOT commit
  to a single carrier representation. Different instances bring their
  own canonical-form function; the UP only sees the abstract
  factorisation property.
- One slice per file-edit per [[annealing-methodology]]; each slice
  typechecks under `--safe --without-K` before the next begins.

## Slices

### Phase A: UP-arrow surface (QU1-QU4)

- QU1: `Substrate.Algebra.Quotient` — the carrier record.
  Equivalence relation + canonical-form function + idempotence +
  respect laws. Substrate-native, no stdlib.
- QU2: `Substrate.Category.UniversalProperty.Quotient.UPArrow` —
  realise quotient-as-UP. Source = "(A, ~, B, respecting f)";
  Target = "factor f̃"; Witness = factorisation + uniqueness.
- QU3: The canonical projection `q : A → A/~` (image of
  canonical-form), and its respect-of-~ property.
- QU4: Phase-A capstone: QuotientUP record landed; ready for
  instance attachment.

### Phase B: Existing instances as QuotientUP (QU5-QU10)

- QU5: Coxeter Word normalize as QuotientUP instance.
- QU6: ℚ (Substrate.Algebra.Q.Reduction) as QuotientUP instance.
- QU7: Conway surreals (≈ⁿ) as QuotientUP instance.
- QU8: V4-Cosets / S₄ / V₄ as QuotientUP instance.
- QU9: F₂ (parity) as QuotientUP instance (ℕ / even-≈).
- QU10: Phase-B capstone: five concrete instances; the UP
  pattern is empirically validated.

### Phase C: CRT as quotient-of-product (QU11-QU16)

- QU11: `QuotientProduct` — the UP saying "quotient by a refinement
  of ~₁ ∩ ~₂ factors through quotient by ~₁ × quotient by ~₂".
- QU12: Coprime-modulus instance setup: parameterise on ℕ m, n with
  gcd witness from Substrate.Algebra.Nat.Bezout.
- QU13: ℤ/(mn) ≅ ℤ/m × ℤ/n as QuotientProduct instance under coprime
  hypothesis.
- QU14: Connect to AbelianPFG: existing AbelianPFG instances now
  inherit CRT structurally.
- QU15: Multi-factor CRT (n-ary): ∏ᵢ ℤ/mᵢ for pairwise-coprime mᵢ.
- QU16: Phase-C capstone: CRT lands as UP instance, no ad-hoc proof.

### Phase D: EEA as morphism in QuotientUP category (QU17-QU22)

- QU17: `QuotientMorphism` — refining equivalences yields
  quotient-arrows (~₁ ⊆ ~₂ ⇒ A/~₁ → A/~₂).
- QU18: EEATrace (already in Substrate.Algebra.Nat.GCD) recast as
  a QuotientMorphism witness. EEA-construction = morphism-builder.
- QU19: Bezout witness as the inverse-map witness of the CRT
  isomorphism (sm + tn = 1 IS the explicit splitting).
- QU20: Substrate-native EEA: rebuild GCD/Bezout under the new
  QuotientMorphism interface, dropping stdlib Data.Nat.DivMod /
  Data.Nat.Divisibility dependencies the current implementation has.
- QU21: Tie back to AbelianPFG: EEA gives the algorithmic content of
  the AbelianPFG product-decomposition.
- QU22: Phase-D capstone: EEA lands as algorithmic structure on
  the QuotientUP category.

### Phase E: Arc closure (QU23-QU25)

- QU23: Integration: register all instances + CRT/EEA in the UP-topos
  catalogue per the UP-arc's pattern (UP6: concrete UP-objects).
- QU24: Memory updates: add `project-quotient-as-up` + retire any
  "CRT/EEA pending" notes from existing memory.
- QU25: Arc capstone.

## Risks

- QU1's canonical-form discipline forces every instance to provide a
  concrete `canonical : A → A`. The Coxeter `normalize` and Q's gcd
  reduction already match this; surreal `≈ⁿ` doesn't have a
  canonical-form function (deferred — surreal numbers are equivalence
  classes by `≈ⁿ` without picking representatives). QU7 may need a
  Setoid-only variant of the UP.
- QU13 requires `ℤ` modulo arithmetic. Currently `Substrate.Algebra.Z`
  is just the carrier; ℤ-mod-m would be a new instance that may need
  to be built up first.
- QU20 is bigger than a slice (it's the in-tree GCD rewrite that the
  previous stdlib-migration arc deferred). May need its own sub-arc.

## Status

Plan written. Execution begins with QU1.
