------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.V4PlaneOrth
--
-- M-11.metric-gauge.v4plane-orth slice. Applies the metric-parametric
-- orthogonality predicate from MetricOrthogonality.agda to a SPECIFIC
-- subspace (V4Plane), exposing the metric-dependence of subspace
-- orthogonal complements.
--
-- **Structural surprise** (the catalog conjecture's metric-dependence
-- made concrete):
--
--   * Under metric-id: e₃ is the V4Plane-orthogonal vector
--     (= the standard chirality axis from M-11.dim3).
--   * Under metric-mixed: e₃ is STILL V4Plane-orthogonal (the d=1
--     off-diagonal coupling lives INSIDE V4Plane, not between V4Plane
--     and e₃).
--   * Under metric-fully-coupled: e₃ is NOT V4Plane-orthogonal!
--     Different metric → different chirality axis: (1, 0, 1) is the
--     V4Plane-orthogonal vector instead.
--
-- This demonstrates that **the chirality axis is a metric-dependent
-- notion**. Catalog-conjecture work (Reserved ↔ SelfDual, etc.) that
-- treats chirality as fixed implicitly chose `metric-id`; other
-- metrics give other chirality identifications.
--
-- Per `feedback_choice_rigidification_in_substrate`: the substrate's
-- existing chirality-as-⟨e₃⟩ identification is gauge-fixed; this slice
-- surfaces alternatives within the 28-metric gauge.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.V4PlaneOrth where
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricFullyCoupled using (metric-fully-coupled)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.BilinearFormOf using (bilinear-form-of)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricMixed using (metric-mixed)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricId using (metric-id)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Type using (SymBilinForm-3)

open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂; ₃)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricOrthogonality

------------------------------------------------------------------------
-- N-1: The "M-orthogonal to V4Plane" predicate.
--
-- V4Plane = ⟨e₀, e₁⟩ = {𝟎ⱽ, e₀, e₁, e₀+e₁}. By bilinearity of
-- bilinear-form-of M, a vector v is M-orthogonal to ALL 4 V4Plane
-- elements iff it's M-orthogonal to the 2 BASIS elements (e₀, e₁).
-- The orthogonality to 𝟎ⱽ is trivial; to e₀+e₁ follows from the
-- other two by bilinearity.
------------------------------------------------------------------------

open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.Pullback
  using (Wide-Meet)
M-orth-to-V4Plane : SymBilinForm-3 → Vector 3 → Set
M-orth-to-V4Plane M v =
  metric-orthogonal M v (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) ×
  metric-orthogonal M v (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ [])

------------------------------------------------------------------------
-- N-2: e₃ is V4Plane-orthogonal under metric-id.
--
-- (This is the standard chirality axis from M-11.dim3; recovered
-- here as the metric-id instance of M-orth-to-V4Plane.)
------------------------------------------------------------------------

e₃-orth-V4Plane-under-metric-id :
  M-orth-to-V4Plane metric-id (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ [])
e₃-orth-V4Plane-under-metric-id = refl , refl

------------------------------------------------------------------------
-- N-3: e₃ is V4Plane-orthogonal under metric-mixed.
--
-- The d=1 off-diagonal coupling in metric-mixed lives INSIDE V4Plane
-- (couples bit 0 with bit 1, both V4-bits); it doesn't pair V4Plane
-- with e₃. So the chirality axis is preserved.
------------------------------------------------------------------------

e₃-orth-V4Plane-under-metric-mixed :
  M-orth-to-V4Plane metric-mixed (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ [])
e₃-orth-V4Plane-under-metric-mixed = refl , refl

------------------------------------------------------------------------
-- N-4: e₃ is NOT V4Plane-orthogonal under metric-fully-coupled.
--
-- The e=1 and f=1 couplings pair e₃ (= bit 2) with both bits 0 and 1
-- of V4Plane. So e₃ is NOT in V4Plane's orthogonal complement under
-- this metric. Witnessed by the explicit nonzero pairing.
------------------------------------------------------------------------

e₃-NOT-orth-e₀-under-metric-fully-coupled :
  bilinear-form-of metric-fully-coupled (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []) (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) ≡ 𝟙
e₃-NOT-orth-e₀-under-metric-fully-coupled = refl

------------------------------------------------------------------------
-- N-5: (1, 0, 1) IS V4Plane-orthogonal under metric-fully-coupled.
--
-- Under metric-fully-coupled, V4Plane's orthogonal complement is
-- ⟨(1, 0, 1)⟩ = {𝟎ⱽ, (1, 0, 1)} — a DIFFERENT 1-dim subspace than
-- the standard chirality axis ⟨e₃⟩.
--
-- Verification:
--   bilinear-form-of metric-fully-coupled (1,0,1) (1,0,0):
--     metric-fully-coupled = (a=1, b=0, c=0, d=1, e=1, f=1)
--     = 1·(1·1 + 1·0 + 1·0) + 0·(1·1+0·0+1·0) + 1·(1·1+1·0+0·0)
--     = 1·1 + 0 + 1·1 = 1 + 1 = 0 ✓
--   bilinear-form-of metric-fully-coupled (1,0,1) (0,1,0):
--     = 1·(1·0+1·1+1·0) + 0·... + 1·(1·0+1·1+0·0)
--     = 1·1 + 0 + 1·1 = 0 ✓
------------------------------------------------------------------------

1-0-1-orth-V4Plane-under-metric-fully-coupled :
  M-orth-to-V4Plane metric-fully-coupled (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ [])
1-0-1-orth-V4Plane-under-metric-fully-coupled = refl , refl

------------------------------------------------------------------------
-- N-6: Capstone — chirality is metric-dependent.
--
-- The "chirality axis" of V4Plane was previously identified as
-- ⟨e₃⟩ in M-11.dim3 (V4Plane.agda, ChiralityAxis.agda). That
-- identification implicitly assumed metric-id orthogonality.
--
-- This slice demonstrates concretely:
--
--   * Under metric-id: chirality axis = ⟨e₃⟩.
--   * Under metric-mixed: chirality axis = ⟨e₃⟩ (preserved).
--   * Under metric-fully-coupled: chirality axis = ⟨(1, 0, 1)⟩
--     — STRUCTURALLY DIFFERENT.
--
-- Under different metrics in the 28-form gauge, V4Plane's orthogonal
-- complement (= the "chirality axis") shifts across the 7 nonzero
-- F₂³ vectors. All 7 1-dim subspaces of F₂³ \ {𝟎ⱽ} are potential
-- chirality axes, gauge-equivalent under the GL(3, F₂) action.
--
-- Implications:
--
--   * The catalog conjecture's "Reserved = signed singletons /
--     Hodge 1-form" identification is metric-dependent. The 8-element
--     SelfDual subspace (in HodgeDim4) inherits its identification
--     from a metric choice; alternative metrics give alternative
--     8-element subspaces, all gauge-equivalent under GL(4, F₂)
--     (extending metric-gauge to dim 4).
--
--   * M-11.dim3's HodgeComplement-Dim3 record uses metric-id-
--     orthogonality; lifting it to a metric-parametric form is a
--     natural follow-on coalgebraic-unfolding slice.
--
--   * The fractal recurrence at the L_metric meta-level: just as
--     the bijection gauge has its alignment-axis meta-symmetry
--     (L3), the metric gauge has chirality-axis selection as its
--     own meta-symmetry. Different chirality choices are gauge-
--     equivalent; rigidifying on ⟨e₃⟩ is the substrate's hidden
--     gauge choice surfaced by this slice.
--
-- Deferred coalgebraic-unfolding slices:
--
--   * `V4Plane-Orth-Family : SymBilinForm-3 → KernelCode 3 ?`:
--     the 28-element family of V4Plane-orthogonal subspaces, one
--     per metric (with collapsed identifications under the 7-element
--     orbit on chirality axes).
--
--   * `Chirality-Axis-At-Metric : SymBilinForm-3 → Vector 3`:
--     the canonical generator of V4Plane's complement under each
--     metric. Computed by a constructive enumeration of "vectors
--     M-orthogonal to e₀ and e₁."
--
--   * `HodgeComplement-Dim3-Parametric : SymBilinForm-3 →
--     HodgeComplement-Dim3-family`: the M-11.dim3 capstone record
--     lifted to a 28-element parametric family.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- N-7: Categorical retrofit — M-orth-to-V4Plane as Wide-Meet over Fin 2.
--
-- Per `feedback_categorical_name_first` and the
-- Substrate.Category.Primitives roadmap. The substrate's binary
-- "orthogonal to e₀ AND orthogonal to e₁" pattern IS exactly the
-- Wide-Meet over the 2-element index set Fin 2 of the
-- orthogonal-to-basis-vector family.
--
-- The categorical handle says: a vector v is V4Plane-orthogonal
-- iff it lies in the meet of the two basis-orthogonality predicates
-- in Sub(Vector 3). Wide-Meet at Fin 2 is the binary case; the same
-- pattern generalises to V4Plane-equivalents in higher dimensions.
------------------------------------------------------------------------


-- The 2-element family: i = zero ↦ orthogonal-to-e₀; i = 1 ↦ -to-e₁.
V4Plane-basis-orth-family : SymBilinForm-3 → Fin 2 → Vector 3 → Set
V4Plane-basis-orth-family M zero       v =
  metric-orthogonal M v (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ [])
V4Plane-basis-orth-family M ₁ v =
  metric-orthogonal M v (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ [])

-- M-orth-to-V4Plane reformulated as the Wide-Meet over Fin 2.
M-orth-to-V4Plane-as-WideMeet : SymBilinForm-3 → Vector 3 → Set
M-orth-to-V4Plane-as-WideMeet M = Wide-Meet (V4Plane-basis-orth-family M)

-- Bridge: existing × form → Wide-Meet form.
M-orth-to-V4Plane→WideMeet :
  (M : SymBilinForm-3) (v : Vector 3) →
  M-orth-to-V4Plane M v → M-orth-to-V4Plane-as-WideMeet M v
M-orth-to-V4Plane→WideMeet M v (orth-e₀ , _)       zero       = orth-e₀
M-orth-to-V4Plane→WideMeet M v (_ , orth-e₁)       ₁ = orth-e₁

-- Bridge: Wide-Meet form → existing × form.
WideMeet→M-orth-to-V4Plane :
  (M : SymBilinForm-3) (v : Vector 3) →
  M-orth-to-V4Plane-as-WideMeet M v → M-orth-to-V4Plane M v
WideMeet→M-orth-to-V4Plane M v wm = wm zero , wm ₁
