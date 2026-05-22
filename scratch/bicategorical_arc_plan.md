# Bicategorical Lift arc (B-arc) — 10-slice plan

Picks up TWO long-running threads:
1. The **Yoneda reverse direction** deferred in Y9 (needs
   naturality on `PresheafMorphism`).
2. The **bicategorification of Z/2** mentioned early in the
   conversation but never materialised.

Both threads land naturally in a single 10-slice arc that
**bicategorifies the language category** built in the Y-arc.
Adding 2-morphisms gives naturality witnesses (closing Y9) AND
connects to the BZ/2 thread (Z/2 as a one-object bicategory)
via the discrete-2-cells case.

## Why this arc

Per [[project-3plus1-parity-universal]] and the early
conversation's BZ/2 insight: bicategorifying the substrate's
F₂-grade structures propagates 2-cell content throughout. The
language category from the Y-arc is the cleanest substrate-
internal place to start: it has well-defined 1-morphisms and a
ready-made candidate for 2-morphisms (the `_≈M_` extensional
equality from Y4).

Per [[feedback-coalgebraic-not-consumer-driven]]: the Y9 reverse
direction's deferral was conditional on naturality machinery; the
bicategorical lift IS the natural place to supply it. The
substrate's existing `Substrate.Category.TwoCategory` /
`Substrate.Category.TwoNaturalTransformation` infrastructure
(developed for codec-arc work) plugs in cleanly.

## Costructure shadows

- **`Language2Morphism`** — promote `_≈M_` from a flat equivalence
  to a proper bicategorical 2-cell record with vertical +
  horizontal composition.
- **`BicategoryOfLanguages`** — the bicategorical bundle
  generalising Y5's CategoryOfLanguages.
- **`NaturalPresheafMorphism`** — refine Y8's PresheafMorphism
  with a naturality witness, enabling the Y9 reverse direction.

## Composition operations

| Op | Signature | Role |
|----|-----------|------|
| `id-2mor` | `(f : LangMor L₁ L₂) → Language2Morphism f f` | identity 2-cell |
| `_∘V_` | vertical composition | f→g ∘V g→h |
| `_∘H_` | horizontal composition | (f→g) at L₁→L₂ × (h→k) at L₂→L₃ |
| `interchange` | the bicategorical coherence law | |
| `よ-2` | bicategorical Yoneda embedding | |

## Entailment claim

```
LanguageMorphism × Language2Morphism × Vertical/Horizontal composition
  × Interchange law
  ⊢ ∀ f, g : LangMor L M. (yoneda-backward f ≅Nat yoneda-backward g)
                          ↔ (f ≈M g)
```

Naturality + bicategorical structure jointly discharge the Y9
reverse direction: the natural-transformation bijection
yoneda-forward / yoneda-backward IS the Yoneda lemma's full
statement.

## Ten slices

Annealing discipline ([[project-annealing-methodology]]).
[[feedback-minimize-stdlib-deps]]-strengthened: substrate-native
throughout.

### Phase 1 — 2-morphisms (B1-B3)

- **B1 `Substrate.Linguistic.Language2Morphism`** — the
  2-morphism record between parallel LanguageMorphisms. Carries
  the extensional-equality data from `_≈M_` plus 2-cell
  composition fields. Connects to
  `Substrate.Category.TwoCategory` if applicable.

- **B2 `Substrate.Linguistic.Vertical`** — vertical composition
  of 2-cells (between same parallel pair).
  `α : f ⇒ g, β : g ⇒ h ⊢ β ∘V α : f ⇒ h`. Identity (`id-2mor`)
  and laws.

- **B3 `Substrate.Linguistic.Horizontal`** — horizontal
  composition (between different parallel pairs at composable
  1-cells). `α : f ⇒ g at L₁→L₂, β : h ⇒ k at L₂→L₃ ⊢
  β ∘H α : h∘f ⇒ k∘g at L₁→L₃`.

### Phase 2 — Coherence + bicategorical record (B4-B5)

- **B4 `Substrate.Linguistic.Interchange`** — the bicategorical
  coherence law: `(β₁ ∘V α₁) ∘H (β₂ ∘V α₂) ≡ (β₁ ∘H β₂) ∘V
  (α₁ ∘H α₂)`. The defining axiom of a bicategory at the
  2-morphism layer.

- **B5 `Substrate.Linguistic.BicategoryOfLanguages`** — the
  bicategorical bundle: objects + 1-morphisms + 2-morphisms +
  ∘V + ∘H + identity-1 + identity-2 + interchange. Generalises
  Y5's CategoryOfLanguages.

### Phase 3 — Yoneda naturality (B6-B8)

- **B6 `Substrate.Linguistic.NaturalPresheafMorphism`** — refine
  Y8's `PresheafMorphism` with a naturality field. Given
  `α : P ⇒ Q` and `f : X → Y`, the naturality square commutes:
  `Q-map f ∘ α-X ≡ α-Y ∘ P-map f`.

- **B7 `Substrate.Linguistic.YonedaNatural`** — show the
  `よ-presheaf-mor` from Y8 produces a NATURAL PresheafMorphism
  for every LanguageMorphism. The naturality square is provable
  by composition associativity (Y4 lemma).

- **B8 `Substrate.Linguistic.YonedaReverse`** — close Y9's
  deferred reverse direction. Given α : NaturalPresheafMorphism
  (よ L) (よ M), prove yoneda-backward (yoneda-forward α) ≅Nat α
  (where ≅Nat is the natural-transformation extensional
  equality). Uses B7's naturality.

### Phase 4 — Capstone (B9-B10)

- **B9 `Substrate.Linguistic.YonedaFull`** — the full Yoneda
  lemma statement + proof bundle: forward AND backward
  directions, with NaturalPresheafMorphism as the codomain
  category. Subsumes Y9.

- **B10 `Substrate.Linguistic.BicategoricalCapstone`** — top-
  level re-export + smoke tests + cross-arc verification that
  the Y-arc's Yoneda machinery extends cleanly to the
  bicategorical setting. Includes a connection note to the BZ/2
  discussion: Z/2 IS the one-object full subcategory of the
  language bicategory whose 1-cells are F₂-graded.

## Substrate primitives engaged

- Substrate.Category.TwoCategory (if applicable)
- Substrate.Category.TwoNaturalTransformation (if applicable)
- The Y-arc's full apparatus (Y1-Y10)
- Substrate.Category.NaturalTransformation (existing primitive)

## Connection to surreals (S-arc)

After both arcs land, the substrate has TWO independent
extensions:
- Numeric carriers (S-arc): birthday-indexed surreals as
  recursive term algebra.
- Categorical depth (B-arc): bicategorical lift of the language
  classification with full Yoneda.

A future arc could combine: surreals as a witness LANGUAGE in
the bicategorical language classification (Conway games as a
free-X-over-basis instance). Or apply bicategorification to
surreals (the natural transfinite hierarchy = a 2-categorical
structure).

## Success criteria

1. All ten B-arc slices typecheck under `--safe --without-K`.
2. B1-B3 establish 2-morphism records + composition.
3. B4 proves interchange.
4. B5 bundles the bicategory.
5. B7 + B8 jointly close the Y9 reverse direction.
6. B9 states the full Yoneda lemma with both directions proven.
7. B10 demonstrates regression: existing Y-arc still works.

## Position in the 20-slice sprint

This B-arc follows the S-arc (surreals). After both land:
- 60 slices on the linguistic family (Lojban + Toki Pona +
  Classification + D-closure + Y-lift + B-bicategorical = 60).
- 10 slices on numeric carriers (surreals).

The substrate has cleanly separated linguistic / numeric / 
codec tracks, each with its own categorical apparatus.
