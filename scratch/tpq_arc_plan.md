# Toki Pona ℚ-retrofit arc (TPQ-arc) — 10-slice plan

Rebuilds Toki Pona's semantic-vector layer with ℚ vectors instead
of F₂, closing the [[feedback-q-over-r-constructive]] deferral and
the original Toki Pona arc's "ℝ deferred until ℚ exists" note.

## Why this arc

The original Toki Pona arc (T-arc) used F₂-vectors for nimi
semantics, with the explicit note that "real distributional Toki
Pona semantics would want ℚ-valued vectors." With Q-arc landed
and FLQ-arc generalising FreeLinearization, the retrofit is now
forced per [[feedback-coalgebraic-not-consumer-driven]].

The ℚ-valued semantics are RICHER than F₂:
- F₂: each nimi activates a discrete bit (presence / absence)
- ℚ: each nimi has a ℚ-weighted contribution (degree of activation)
- Polysemy: ℚ-vector blends across multiple semantic axes
- Modifier composition: bilinear with ℚ coefficients

## Costructure shadows

- **`ℚ-NimiSpace`** — ℚ-vector-valued semantic carrier (sister to
  the F₂ `NimiSpace`).
- **`ℚ-ModifierBilinear`** — bilinear composition over ℚ (this
  one IS genuinely bilinear, unlike the F₂ original — see the
  D1 `WithBasisAction` discussion).
- **F₂-ℚ forgetful-functor** — bridge between the two semantics
  for cross-arc continuity.

## Ten slices

### Phase 1 — ℚ-carrier setup (TPQ1-TPQ3)

- **TPQ1 `Substrate.TokiPona.QSemanticSpace`** — sister to T1
  SemanticSpace but over ℚ. `Q-SemVec m = Vector ℚ m` + the
  abelian-group laws inherited from ℚ-Vector.
- **TPQ2 `Substrate.TokiPona.QNimiSpace`** — sister to T3
  NimiSpace via FLQ7's ℚ-FreeLinearization. Each nimi maps to
  a ℚ-basis vector; the linear extension lifts arbitrary
  nimi-image maps.
- **TPQ3 `Substrate.TokiPona.QModifierBilinear`** — the bilinear
  modify over ℚ. Unlike the F₂ original, this IS genuinely
  bilinear (no characteristic-2 self-inverse collapse).

### Phase 2 — Composition layer (TPQ4-TPQ6)

- **TPQ4 `Substrate.TokiPona.QTokiSentence`** — ℚ-valued sentence
  record + interpret function.
- **TPQ5 `Substrate.TokiPona.QParticles`** — particle markers as
  ℚ-graded structural data (still discrete bit-flags; particles
  don't get richer in ℚ).
- **TPQ6 `Substrate.TokiPona.QLinearity`** — coherence record
  packaging the ℚ-side bilinearity + identity laws.

### Phase 3 — Universal property + bridge (TPQ7-TPQ8)

- **TPQ7 `Substrate.TokiPona.QLinearAlgebra`** — sister to T8
  LinearAlgebra; provides the universal-property record for the
  ℚ-NimiSpace.
- **TPQ8 `Substrate.TokiPona.F2-to-Q-Forget`** — forgetful
  functor: every F₂ Toki Pona semantic value lifts to a ℚ one
  (via 0↦0/1, 1↦1/1). Demonstrates that the original arc is a
  sub-instance of the ℚ-version.

### Phase 4 — Fragment + capstone (TPQ9-TPQ10)

- **TPQ9 `Substrate.TokiPona.QFragment`** — worked examples
  with ℚ semantics: "soweli lili" with rational weight
  combinations, demonstrating polysemy blending that F₂ couldn't
  express.
- **TPQ10 `Substrate.TokiPona.QCapstone`** — re-export +
  cross-arc summary + connection note: the F₂ Toki Pona arc
  remains the FRAGMENT for substrate-internal demonstrations; the
  ℚ version is the FULL semantic carrier for any consumer
  needing richer semantics.

## Substrate primitives engaged

- Q-arc: Substrate.Algebra.Q.{Vector,Linear} (and ℚ itself)
- FLQ-arc: Substrate.Category.FreeLinearizationR + Q instance
  (slices 1-10 of this 20-slice sprint)
- Original Toki Pona arc: Substrate.TokiPona.* (sister structures)

## Success criteria

1. All ten TPQ slices typecheck under `--safe --without-K`.
2. ℚ-NimiSpace + ℚ-ModifierBilinear demonstrate richer semantics
   than F₂.
3. F₂-to-ℚ forget functor proves the original arc is a sub-
   instance.
4. Worked examples (TPQ9) demonstrate ℚ-weighted polysemy that
   F₂ couldn't express.
5. The original F₂ Toki Pona arc remains intact (no breakage).

## Deferred (out of arc)

- Lojban ℚ-retrofit (Lojban doesn't naturally want ℚ; deferred
  because the language's discrete word-algebra structure isn't
  enriched by going to ℚ).
- Solresol ℚ-retrofit (similar — cyclic-group structure doesn't
  want ℚ).
- ℚ-FreeLinearization for ℝ-valued limit (ℝ deliberately not
  built; surreal-valued limits are a future arc).
- Distributional-semantics learning algorithms (out of substrate
  scope; pedagogy is constructive inference rules, not learned
  embeddings — per [[feedback-continuous-via-discrete-inference-rules]]).
