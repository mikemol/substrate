# FreeLinearization-over-ℚ arc (FLQ-arc) — 10-slice plan

Generalises Substrate.Category.FreeLinearization from F₂ to a
parametric "Free-linear-over-R" primitive, then instantiates at
F₂ (existing) and ℚ (just-built Q-arc).

## Why this arc

Per [[project-freelinearization-names-linear-from-images]]: the
substrate's #6 categorical primitive captures "any function from a
finite basis to a target vector space extends uniquely to a linear
map." Currently the primitive is hardcoded to F₂. With the Q-arc
landed, generalising opens up:
- Toki Pona with ℚ-valued semantic vectors (TP-ℚ-arc, slices 11-20)
- Future arcs needing distributional semantics
- Any constructive linear algebra over richer-than-F₂ carriers

Per [[feedback-categorical-name-first]]: "free module over a ring"
is the universal name; F₂-FreeLinearization is the R=F₂ instance.

## Costructure shadows

- **`LinearAlgebra`** record bundling (Vector, Linear, basis,
  preserves-+, preserves-*ₛ) for an abstract scalar carrier R.
- **`FreeLinearization-R`** parametric over R via LinearAlgebra
  instance.
- F₂ and ℚ as concrete instances.

## Ten slices

### Phase 1 — Abstract carrier (FLQ1-FLQ3)

- **FLQ1 `Substrate.Category.LinearAlgebra`** — abstract record
  bundling the scalar type R + Vector R + Linear R + basis +
  preserves laws. The "category of free modules over R" data.
- **FLQ2 `Substrate.Category.FreeLinearizationR`** — parametric
  free-linearization record over LinearAlgebra instance. Images
  map → unique linear extension → basis-agreement + uniqueness.
- **FLQ3 `Substrate.Category.FreeLinearizationR.FromImages`** —
  parametric `free-linearize-R` constructor (analog of the F₂
  `free-linearize`).

### Phase 2 — F₂ instance (FLQ4-FLQ5)

- **FLQ4 `Substrate.Algebra.F2.AsLinearAlgebra`** — package the
  existing F₂-Vector + F₂-Linear into a LinearAlgebra instance.
- **FLQ5 `Substrate.Category.FreeLinearizationR.F2Bridge`** —
  bridge showing the parametric FreeLinearizationR at the F₂
  instance reproduces (up to record-shape) the existing
  Substrate.Category.FreeLinearization. Real Agda content: an
  equivalence at the canonical-image construction.

### Phase 3 — ℚ instance (FLQ6-FLQ8)

- **FLQ6 `Substrate.Algebra.Q.AsLinearAlgebra`** — package Q8's
  ℚ-Vector + Q9's ℚ-Linear into a LinearAlgebra instance.
- **FLQ7 `Substrate.Category.FreeLinearizationR.QInstance`** —
  the ℚ-instantiation of FreeLinearizationR. Concretely:
  `free-linearize-ℚ : (Fin n → Vector ℚ m) → ℚ-Linear n m`.
- **FLQ8 `Substrate.Category.FreeLinearizationR.QExamples`** —
  worked examples: a 3-dimensional ℚ-basis with rational entries
  extends to a rational linear map.

### Phase 4 — Capstone (FLQ9-FLQ10)

- **FLQ9 `Substrate.Category.FreeLinearizationR.SmokeTests`** —
  cross-arc verification that the F₂ and ℚ instances agree on the
  shared structural shape (LinearAlgebra fields populated; basis
  embedding consistent).
- **FLQ10 `Substrate.Category.FreeLinearizationR.Capstone`** —
  re-export + summary; TP-ℚ-arc (slices 11-20) consumes
  FreeLinearizationR-ℚ for Toki Pona's retrofit.

## Substrate primitives engaged

- Substrate.Category.FreeLinearization (the F₂ original)
- Substrate.Algebra.F2.{Vector,Linear,Linear.FromImages}
- Substrate.Algebra.Q.{Vector,Linear} (Q8, Q9)
- Substrate.Category.Morphism (potentially for LinearAlgebra
  bundling)

## Success criteria

1. All ten FLQ slices typecheck under `--safe --without-K`.
2. F₂ instance reproduces existing FreeLinearization structure.
3. ℚ instance demonstrates rational-linear extension.
4. Worked example with explicit rational basis-image map.
5. Capstone re-export ready for TP-ℚ-arc consumption.

## Deferred

- Universal-property uniqueness proof for ℚ-Linear (Q9 supplies
  the structure; ℚ-linear-extensionality is a follow-up lemma).
- Bridge to FreeLinearization-over-ℤ (would need ℤ-module
  primitives; deferred to a future ring-of-integers arc).
- ℝ instance (deliberately not built per
  [[feedback-q-over-r-constructive]]).
