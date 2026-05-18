# Substrate.Category.Primitives — DBE roadmap

**Target.** Two-prong infrastructure layer:

- **Prong A — Audit.** Surface latent category-theoretic constructs in the existing substrate. Per `feedback_categorical_name_first`: where the substrate has implicitly invented axioms that ARE the universal property of a standard categorical concept, name them with the established categorical name and let downstream substrate code cite the primitive.

- **Prong B — Primitives.** Introduce CT primitive inference rules as `Substrate.Category.*` modules. Each primitive consists of (data, universal property as inference rule, optional derived rules). Existing substrate sites become *instances* of primitives via retrofit lemmas.

**Discipline.** Per `feedback_categorical_name_first`: use established categorical names whose universal property IS the inference rule. Prefer Beck-Chevalley over "quotient-curvature"; subcoalgebra over "coalgebraic-stability"; equalizer over "kernel-spec"; etc.

**Coalgebraic, not consumer-driven.** Primitives are added in dependency order to surface structure, not "if downstream consumers need them" (per `feedback_coalgebraic_not_consumer_driven`).

---

## Primitive dependency ordering

Each primitive ~150-250 LoC. Numbered by build order:

### 1. `Substrate.Category.Coalgebra` — endomap coalgebra, fixed points, invariant subsets ★ FIRST SLICE

**Universal property:**
- `FixedPoint γ x ⇔ γ x ≡ x`
- `InvariantSubset γ S ⇔ ∀ x. S x → S (γ x)`
- (Singleton {x} is invariant ⇔ x is a fixed point.)

**Retrofit sites:**
- `s₁-stabilises-metric-id` → `metric-id-fixed-by-cong-act-s₁ : FixedPoint (congruence-act s₁) metric-id`
- `s₂-stabilises-metric-id` → analogous
- `s₁∘s₂-stabilises-metric-id` → analogous
- (Future: dim-4 stabilisers when those slices land.)

**Inference rule it provides:** "metric-id is a fixed point of every g in the stabiliser subgroup." Plus the deferred `congruence-compose` lemma, when combined with `FixedPoint-of-compose : FixedPoint γ₁ x → FixedPoint γ₂ x → FixedPoint (γ₁ ∘ γ₂) x`, automates the closure cascade — eliminates the need for separate StabiliserClosure proofs.

**Status:** Slice in progress.

---

### 2. `Substrate.Category.Equalizer` — kernel-of-(f, g) as universal property

**Universal property:**
- `IsEqualizer e f g ⇔ f ∘ e ≡ g ∘ e` (object property) plus universal-mapping property.
- For linear maps: `Kernel-Of M = Equalizer (M·_) (𝟘 ⋆_)`.

**Retrofit sites:**
- `NonDegenerate-4` and `NonDegenerate` kernel-free predicates: `M is non-degenerate ⇔ Kernel-Of M = {𝟎ⱽ}`.
- `pair-metric-id-4-with-eᵢ` lemmas reduce to "v is in kernel of metric-id-4 iff each pairing vanishes" — equalizer universal property over the basis indices.

**Inference rule:** non-degeneracy as terminal-kernel, equalizer universal mapping.

---

### 3. `Substrate.Category.Pullback` — wide pullback / meet in Sub(X)

**Universal property:**
- Standard pullback square universal property.
- For subobjects of X: meet = pullback in Sub(X).

**Retrofit sites:**
- `3+1 parity universal` — the "+1" element is the intersection of three orbit predicates (V₄-orbit ∩ chirality-axis ∩ Hodge-dual). Currently observed per-instance; pullback primitive names it once.
- `OrbitKey` 6-vs-1 decompositions.
- `M-orth-to-V4Plane` from V4PlaneOrth.agda: intersection of orthogonality predicates.

**Inference rule:** mapping into the pullback ↔ compatible families of mappings into components.

---

### 4. `Substrate.Category.Adjunction` — adjoint functor pair with unit/counit

**Universal property:**
- Standard `L ⊣ R` with `Hom(L A, B) ≅ Hom(A, R B)` naturally.

**Retrofit sites:**
- `linear-from-images` ⊣ `images-of-linear` — already the M-3.5 "universal property discipline" foundation; renaming as an adjunction makes downstream uses cite the universal property directly.
- Coxeter presentation ⊣ Cayley graph (future, when Cayley-graph constructor lands).
- Free linearization (future Prong B work).

**Inference rule:** transposition; left adjoints preserve colimits; right adjoints preserve limits.

---

### 5. `Substrate.Category.BeckChevalley` — non-commuting quotient square + 2-cell

**Universal property:**
- For a pullback square of right adjoints, the canonical 2-cell between transpose composites is iso ("Beck-Chevalley condition holds") or not iso ("Beck-Chevalley fails, with curvature").

**Retrofit sites:**
- `project_3plus1_parity_universal` recurring at successive meta-levels — each is a Beck-Chevalley failure witness between two quotient-collapse orders.
- The sacrifice ladder's rung transitions (per `project_reserved_selfdual_bijection_gauge`).
- The tetrative metacircularity tower's level transitions (`project_tetrative_metacircularity`).

**Inference rule:** the BC 2-cell's iso/non-iso status is the substrate's recurring "non-commutativity of quotients" observation, now namable as a categorical witness type.

**Depends on Adjunction.**

---

### 6. `Substrate.Category.FreeLinearization` — Graph → R-Mod free functor

**Universal property:**
- Adjoint to underlying-graph functor: linear maps on Free(G) ↔ graph homomorphisms from G.

**Retrofit sites:**
- (Prong B begins.) Bridges to spectral side per `feedback_continuous_via_discrete_inference_rules` — the inference rule for constructing a graph Laplacian / adjacency operator as a Linear, parametric in the carrier ring.
- Substrate currently F₂-only; this generalizes Linear over any commutative semiring.

**Inference rule:** free construction's universal property. Specializing the carrier ring to F₂ recovers existing infrastructure; specializing to ℚ or ℝ enables spectral-side construction RULES (not contents).

**Depends on Adjunction.**

---

## Audit checklist (Prong A scan)

For each existing substrate module, scan for these patterns:

- **Fixed-point-shaped:** `f x ≡ x` with `f` an action/endomap → candidate for `FixedPoint`.
- **Kernel-free-shaped:** `(∀ w. f v w ≡ 𝟘) → v ≡ 𝟎ⱽ` → candidate for `Equalizer`/`Kernel`.
- **Triple-intersection-shaped:** Σ over 2+ predicates → candidate for `Pullback`/meet.
- **Free-construction-shaped:** `from-images` / `from-basis-data` builders → candidate for `Adjunction`.
- **Non-commuting-quotient-shaped:** any observation that "going through A first vs B first gives different orbit classes" → candidate for `BeckChevalley`.
- **Universal-property-shaped:** any "uniquely determined by ⋯" claim → candidate for whichever standard universal property matches.

For each match, record: (substrate location, candidate primitive, universal-property-citation, retrofit estimate).

---

## Status

- 2026-05-18: Roadmap created.
- 2026-05-18: Primitive #1 (Coalgebra/FixedPoint) landed (commit 8ce75bf). Retrofits: 3 metric-id stabiliser sites wrap as FixedPoint instances.
- 2026-05-18: Primitive #2 (Equalizer) landed. Retrofits: `In-Kernel C v` from `Substrate.Algebra.F2.Code` bridges to `Kernel-At (apply (parity-check C)) 𝟎ⱽ v` via a two-direction wrapper. FixedPoint↔IsEqualised bridge connects primitives #1 and #2 categorically. NonDegenerate-4 retrofit deferred (requires primitive #3 Pullback for the per-w intersection structure).
- 2026-05-18: Primitive #3 (Pullback) landed. Defines binary `Pullback-Of` + `Wide-Meet` for family-indexed intersection. Includes pullback↔equalizer bridge connecting primitives #2 and #3. Retrofits deferred to next annealing step (V4PlaneOrth's `M-orth-to-V4Plane` as binary pullback / wide meet; NonDegenerate-4 radical as wide meet of per-w equalizers).

---

## Memory connections

- `feedback_categorical_name_first` — discipline rule motivating this work
- `feedback_continuous_via_discrete_inference_rules` — bridges Prong B
- `feedback_coalgebraic_not_consumer_driven` — primitive ordering rule
- `feedback_universal_property_discipline` — pre-existing M-3.5 universal-property work that this layer formalizes
- `project_eliza_concept_orbit_catalog` — origin of the categorical-name observation
- `project_3plus1_parity_universal` — the recurring observation that BeckChevalley will name
- `project_tetrative_metacircularity` — the meta-level ladder that BeckChevalley will witness across
