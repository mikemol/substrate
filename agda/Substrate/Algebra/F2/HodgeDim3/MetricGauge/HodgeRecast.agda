------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.HodgeRecast
--
-- M-11.metric-gauge.hodge-recast slice. Surfaces the previously-hidden
-- metric-id gauge choice in the existing `_·F_` dot product
-- (DotProduct.agda).
--
-- Before this slice: `_·F_ : Vector n → Vector n → F₂` was defined
-- as the standard sum-of-products dot product, used implicitly
-- throughout (V4Plane orthogonality, ChiralityAxis orthogonality,
-- HodgeComplement-Dim3) WITHOUT acknowledging that this is one of
-- 28 possible non-degenerate symmetric bilinear forms — a gauge
-- choice.
--
-- After this slice: at n=3, `_·F_ ≡ bilinear-form-of metric-id`
-- explicitly. The recasting exposes the implicit gauge choice, making
-- the substrate gauge-honest about its existing Hodge structure.
-- Alternative metrics (metric-mixed, metric-fully-coupled, or any of
-- the other 25 non-degenerate forms) give structurally different
-- bilinear forms / orthogonality structures.
--
-- Per `feedback_choice_rigidification_in_substrate`: every implicit
-- gauge is rigidification by neglect; surfacing it IS the work
-- (per `feedback_coalgebraic_not_consumer_driven` — unfolding the
-- structure that's already there).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.HodgeRecast where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.DotProduct using (_·F_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge

------------------------------------------------------------------------
-- N-1: The recast lemma.
--
-- At n=3, the standard dot product `_·F_` equals
-- `bilinear-form-of metric-id`.
--
-- Proof: both sides unfold to v₀·w₀ + v₁·w₁ + v₂·w₂ after F₂
-- arithmetic. The LHS comes from sum-F₂ over Fin 3; the RHS comes
-- from the bilinear-form-of formula instantiated at metric-id's
-- diagonal entries.
------------------------------------------------------------------------

-- DEMOTED to instantiation. The original 28-LoC LHS→canonical /
-- RHS←canonical bridging proof at dim 3 is now a one-line corollary
-- of the generic HodgeRecast (`·F-eq-metric-id-bilin-generic` in
-- Substrate.Algebra.F2.SymBilinForm.HodgeRecast) chained with the
-- bilinear-form-of-metric-id-bridge from GenericBridge.
--
-- Original proof preserved in git history at fb7ce42 (HodgeRecast
-- pre-demotion commit).

open import Substrate.Algebra.F2.SymBilinForm.HodgeRecast
  using (·F-eq-metric-id-bilin-generic)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.GenericBridge
  using (bilinear-form-of-metric-id-bridge)

·F-eq-metric-id-bilin :
  (v w : Vector 3) → v ·F w ≡ bilinear-form-of metric-id v w
·F-eq-metric-id-bilin v w =
  trans (·F-eq-metric-id-bilin-generic v w)
        (sym (bilinear-form-of-metric-id-bridge v w))

------------------------------------------------------------------------
-- N-2: Concrete demonstration of metric-dependence.
--
-- For specific v, w, compute the bilinear forms under two different
-- metrics and observe they're STRUCTURALLY DIFFERENT functions.
-- This demonstrates that `_·F_` (= metric-id) is one of 28 inequivalent
-- gauge choices, and that the orthogonality structure depends on
-- which metric is chosen.
------------------------------------------------------------------------

-- Under metric-id (= standard dot product), e₀ and e₁ are orthogonal.
e₀-perp-e₁-under-metric-id :
  bilinear-form-of metric-id (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []) ≡ 𝟘
e₀-perp-e₁-under-metric-id = refl

-- Under metric-mixed (where d = 1, the (0,1)-coupling is nonzero),
-- e₀ and e₁ are NOT orthogonal — their pairing is 𝟙, not 𝟘.
e₀-not-perp-e₁-under-metric-mixed :
  bilinear-form-of metric-mixed (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []) ≡ 𝟙
e₀-not-perp-e₁-under-metric-mixed = refl

-- Under metric-fully-coupled, every basis-vector pairing is nonzero.
e₀-pair-e₁-under-metric-fully-coupled :
  bilinear-form-of metric-fully-coupled (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []) ≡ 𝟙
e₀-pair-e₁-under-metric-fully-coupled = refl

------------------------------------------------------------------------
-- N-3: Capstone documentation.
--
-- The existing `_·F_` is now formally recognized as ONE of 28 gauge-
-- equivalent bilinear forms over F₂³ — the metric-id instance. Every
-- downstream construction that uses `_·F_` (orthogonality predicates,
-- Hodge ★ at n=3, etc.) implicitly inherits the metric-id gauge
-- choice.
--
-- Alternative metrics give:
--
--   * Different orthogonality structures: under metric-mixed, e₀ and
--     e₁ are NOT orthogonal even though they're orthogonal under
--     metric-id. The "perpendicular subspace to e₃" depends on the
--     metric.
--
--   * Different Hodge ★ at the SUBSPACE level: in F₂³, the Hodge dual
--     of a 1-dim subspace ⟨v⟩ is the 2-dim "orthogonal complement
--     under THIS metric." Different metrics → different complements.
--
--   * Different "self-dual" bivector structures (at n=4) when the
--     metric is lifted to Λ²(F₂⁴).
--
-- Recasting `_·F_` as the metric-id instance does NOT change the
-- existing code's behavior — it surfaces the previously-implicit
-- gauge choice, making the substrate gauge-honest about it.
--
-- Per the L_metric meta-level: the 28-element metric gauge is now
-- exposed as parametrizing the existing Hodge / orthogonality work.
-- Downstream Hodge constructions that want to be metric-parametric
-- can use `bilinear-form-of M` for arbitrary M ∈ SymBilinForm-3
-- (with NonDegenerate M, when invertibility matters).
--
-- Deferred coalgebraic-unfolding follow-ons:
--
--   * Metric-parametric Hodge ★: `hodge-star-via M` parametrising
--     the existing HodgeDim3 / HodgeDim4 construction.
--   * Metric-parametric V4Plane: the "V₄-plane" depends on which
--     metric defines orthogonality.
--   * Demonstration that under different metrics, different subsets
--     of F₂³ are "self-dual" — the 8-element SelfDual subspace
--     changes with the metric (28 such subspaces total, all gauge-
--     equivalent under GL(3, F₂)).
--
-- See M-11.metric-gauge.DBE.md for the full coalgebraic-unfolding
-- roadmap.
------------------------------------------------------------------------
