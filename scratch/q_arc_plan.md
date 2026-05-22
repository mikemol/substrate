# Constructive ℚ arc (Q-arc) — 10-slice plan

Picks up [[feedback-q-over-r-constructive]]: when the substrate
needs a richer numeric carrier than F₂, prefer ℚ over ℝ because
rationals retain their decision structure (num/denom, decidable
equality, finite construction) that ℝ collapses.

## Why this arc

Three converging threads:
1. The F₂-vector encoding of Toki Pona's polysemy is honest but
   limits semantic richness; ℚ-vectors would be a natural lift
   (deferred per the linguistic Rosetta arc).
2. The conway surreal arc (S1-S10) needs richer numeric carriers
   for arithmetic operations beyond Day-1.
3. The MCP / decomposition + several codec arcs touch quantities
   that are naturally ℚ-valued but currently encoded ad-hoc.

Per [[feedback-categorical-name-first]]: "constructive ℚ" is the
standard, predicative-friendly rationals via integer pair quotient.
Substrate-native (no stdlib Data.Rational heavy ecosystem) per
[[feedback-minimize-stdlib-deps]]-strengthened.

## Costructure shadows

- **`ℤ`** (substrate-native integers) — if a substrate ℤ isn't
  already in use, build a minimal one (Q1).
- **`ℚ`** as a (numerator : ℤ, denominator : positive ℕ) record.
- **Reduction**: gcd-normalised representatives.
- **`ℚ-Vector` / `ℚ-Linear`** — sister to F₂.Vector / F₂.Linear.

## Ten slices

### Phase 1 — ℤ + ℚ carrier (Q1-Q3)

- **Q1 `Substrate.Algebra.Z`** — substrate-native ℤ via ℕ + sign
  enum (`+` / `−`), with `+0 ≡ −0` quotient handled by smart
  constructor or convention. Decidable equality, ordering.
- **Q2 `Substrate.Algebra.Q`** — ℚ as (n : ℤ, d : ℕ\{0}) record;
  smart constructor enforces d > 0; canonical-form quotient via
  gcd reduction (deferred to Q4 if too heavy for one slice).
- **Q3 `Substrate.Algebra.Q.DecidableEq`** — decidable equality
  on canonical ℚ representatives.

### Phase 2 — Arithmetic (Q4-Q6)

- **Q4 `Substrate.Algebra.Q.Reduction`** — gcd-based reduction
  to canonical form. Uses ℕ gcd (substrate-native or basic stdlib).
- **Q5 `Substrate.Algebra.Q.Arithmetic`** — addition (a/b + c/d
  = (ad + bc)/bd), negation, multiplication, division (limited;
  not on zero divisor). Each operation reduced.
- **Q6 `Substrate.Algebra.Q.Order`** — `_≤_` via cross-multiplication
  on the canonical form.

### Phase 3 — Embeddings (Q7)

- **Q7 `Substrate.Algebra.Q.Embeddings`** — `ℕ → ℚ` (n ↦ n/1),
  `ℤ → ℚ`, plus inverse-where-possible: `ℚ-as-ℤ-when-d=1`.

### Phase 4 — ℚ-Vector + ℚ-Linear (Q8-Q9)

- **Q8 `Substrate.Algebra.Q.Vector`** — `Vector n = Vec ℚ n` (sister
  to F₂.Vector). Componentwise operations.
- **Q9 `Substrate.Algebra.Q.Linear`** — ℚ-linear maps (sister to
  F₂.Linear). Preserves-+ + preserves-scalar-mult.

### Phase 5 — Capstone (Q10)

- **Q10 `Substrate.Algebra.Q.Capstone`** — top-level re-export +
  smoke tests + connection note to FreeLinearization (would
  generalise from F₂ to ℚ as a future arc).

## Success criteria

1. All ten slices typecheck under `--safe --without-K`.
2. ℚ arithmetic landed (+/−/·/÷, with caveats on ÷).
3. Decidable equality + order proven.
4. ℕ and ℤ embed into ℚ.
5. ℚ-Vector + ℚ-Linear sister structures available.

## Deferred (out of arc)

- FreeLinearization-over-ℚ (parametric generalisation of the F₂ one).
- ℚ → ℝ forgetful functor (per [[feedback-q-over-r-constructive]],
  ℝ is deliberately not reached).
- Toki Pona retrofit with ℚ-vectors.
- Conway surreal arithmetic with ℚ-valued operations.

These surface in follow-up arcs when consumers force them.
