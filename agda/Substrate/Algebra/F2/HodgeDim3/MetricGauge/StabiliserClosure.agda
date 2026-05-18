------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.StabiliserClosure
--
-- M-11.metric-gauge.stabiliser-closure-3-cycle slice. Demonstrates
-- composition closure of the metric-id stabiliser by proving that
-- the 3-cycle `s₁ ∘L s₂` (= S₃'s order-3 generator) stabilises
-- metric-id under the GL(3, F₂) congruence action.
--
-- Background: M-11.metric-gauge.stabiliser established that s₁ and
-- s₂ (the 2 Coxeter generators of S₃) individually stabilise
-- metric-id. The Coxeter presentation ⟨s₁, s₂ | s₁² = s₂² = (s₁s₂)³
-- = e⟩ implies all compositions also stabilise. This slice witnesses
-- the s₁∘Ls₂ composition concretely.
--
-- The composition s₁∘Ls₂ acts on basis vectors as the cyclic shift:
--
--   e₀ ↦ apply s₁ (apply s₂ e₀) = apply s₁ e₀ = e₁ = (0, 1, 0)
--   e₁ ↦ apply s₁ (apply s₂ e₁) = apply s₁ e₂ = e₂ = (0, 0, 1)
--   e₂ ↦ apply s₁ (apply s₂ e₂) = apply s₁ e₁ = e₀ = (1, 0, 0)
--
-- = the cyclic permutation 0 → 1 → 2 → 0. Three iterations give the
-- identity (matching (s₁s₂)³ = e in the Coxeter presentation).
--
-- The full stabiliser group has 6 elements: e, s₁, s₂, s₁∘Ls₂,
-- s₂∘Ls₁, and s₁∘Ls₂∘Ls₁ = s₂∘Ls₁∘Ls₂. The other 2 compositions
-- (s₂∘Ls₁ and s₁∘Ls₂∘Ls₁) follow the same template; deferred to a
-- follow-on stabiliser-closure-full slice or subsumed by the general
-- congruence-compose lemma when that's formalised.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.StabiliserClosure where

open import Data.Fin using (Fin; zero; suc)
open import Data.Vec using ([]; _∷_; lookup)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
  using (apply-linear-from-images-basis)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
open import Substrate.Category.Coalgebra
  using (FixedPoint)

------------------------------------------------------------------------
-- N-1: Per-basis apply reductions for s₁ ∘L s₂.
--
-- apply (s₁ ∘L s₂) v = apply s₁ (apply s₂ v) (by definition of ∘L's
-- apply). For v = basis i, we use s₂-on-eᵢ to reduce the inner apply,
-- then s₁-on-eⱼ (where j is determined by where s₂-images sent i) to
-- reduce the outer.
--
-- The key insight: s₂-images i happens to be a basis vector (s₂ is
-- a permutation), so apply s₁ (s₂-images i) ≡ s₁-images (s₂-permuted-i).
------------------------------------------------------------------------

apply-s₁∘s₂-on-e₀ : apply (s₁ ∘L s₂) (basis zero) ≡ (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ [])
apply-s₁∘s₂-on-e₀ =
  -- s₂ e₀ = e₀ (= (𝟙∷𝟘∷𝟘∷[]) = basis zero by refl);
  -- s₁ e₀ = e₁ = (𝟘∷𝟙∷𝟘∷[])
  trans (cong (apply s₁) s₂-on-e₀) s₁-on-e₀

apply-s₁∘s₂-on-e₁ : apply (s₁ ∘L s₂) (basis (suc zero)) ≡ (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ [])
apply-s₁∘s₂-on-e₁ =
  -- s₂ e₁ = e₂ (= (𝟘∷𝟘∷𝟙∷[]) = basis (suc (suc zero)) by refl);
  -- s₁ e₂ = e₂ = (𝟘∷𝟘∷𝟙∷[])
  trans (cong (apply s₁) s₂-on-e₁) s₁-on-e₂

apply-s₁∘s₂-on-e₂ : apply (s₁ ∘L s₂) (basis (suc (suc zero))) ≡ (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ [])
apply-s₁∘s₂-on-e₂ =
  -- s₂ e₂ = e₁ (= (𝟘∷𝟙∷𝟘∷[]) = basis (suc zero) by refl);
  -- s₁ e₁ = e₀ = (𝟙∷𝟘∷𝟘∷[])
  trans (cong (apply s₁) s₂-on-e₂) s₁-on-e₁

------------------------------------------------------------------------
-- N-2: s₁ ∘L s₂ stabilises metric-id.
--
-- Same entry-by-entry template as s₁-stabilises-metric-id (from
-- Stabiliser.agda), with apply-(s₁∘Ls₂)-on-eᵢ replacing s₁-on-eᵢ.
--
-- The composition's cyclic-shift action permutes the diagonal
-- entries of metric-id (which are all 𝟙) and preserves the
-- off-diagonals (all 𝟘), so the form is preserved structurally.
------------------------------------------------------------------------

s₁∘s₂-stabilises-metric-id :
  congruence-act (s₁ ∘L s₂) metric-id ≡ metric-id
s₁∘s₂-stabilises-metric-id = ≡-from-lookup _ _ goal
  where
    goal : (i : Fin 6) →
           lookup (congruence-act (s₁ ∘L s₂) metric-id) i ≡ lookup metric-id i
    goal zero =
      -- a' = bilinear-form-of metric-id ((s₁∘Ls₂) e₀) ((s₁∘Ls₂) e₀)
      --    = bilinear-form-of metric-id (0,1,0) (0,1,0) = 1 = a
      cong (λ x → bilinear-form-of metric-id x x) apply-s₁∘s₂-on-e₀
    goal (suc zero) =
      cong (λ x → bilinear-form-of metric-id x x) apply-s₁∘s₂-on-e₁
    goal (suc (suc zero)) =
      cong (λ x → bilinear-form-of metric-id x x) apply-s₁∘s₂-on-e₂
    goal (suc (suc (suc zero))) =
      trans (cong (λ x → bilinear-form-of metric-id x (apply (s₁ ∘L s₂) (basis (suc zero)))) apply-s₁∘s₂-on-e₀)
            (cong (bilinear-form-of metric-id (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ [])) apply-s₁∘s₂-on-e₁)
    goal (suc (suc (suc (suc zero)))) =
      trans (cong (λ x → bilinear-form-of metric-id x (apply (s₁ ∘L s₂) (basis (suc (suc zero))))) apply-s₁∘s₂-on-e₀)
            (cong (bilinear-form-of metric-id (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ [])) apply-s₁∘s₂-on-e₂)
    goal (suc (suc (suc (suc (suc zero))))) =
      trans (cong (λ x → bilinear-form-of metric-id x (apply (s₁ ∘L s₂) (basis (suc (suc zero))))) apply-s₁∘s₂-on-e₁)
            (cong (bilinear-form-of metric-id (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ [])) apply-s₁∘s₂-on-e₂)

------------------------------------------------------------------------
-- N-3: Capstone documentation.
--
-- The stabiliser of metric-id under GL(3, F₂) congruence has 6
-- elements (= S₃ via Coxeter presentation):
--
--   e                  identity
--   s₁                 swap (0, 1) — basis transposition
--   s₂                 swap (1, 2) — basis transposition
--   s₁ ∘L s₂           cyclic shift 0 → 1 → 2 → 0  ← this slice
--   s₂ ∘L s₁           cyclic shift 0 → 2 → 1 → 0
--   s₁ ∘L s₂ ∘L s₁     swap (0, 2)
--   (= s₂ ∘L s₁ ∘L s₂)
--
-- Each element stabilises metric-id because basis-permutations
-- preserve the diagonal-identity (sum-of-squares) bilinear form
-- structurally. The 2 Coxeter generators (s₁, s₂) were established
-- in Stabiliser.agda; this slice adds the 3-cycle (s₁ ∘L s₂); the
-- remaining elements (s₂∘Ls₁, s₁∘Ls₂∘Ls₁) follow the same template
-- and are deferred.
--
-- **Structural payoff at L_metric:**
--
--   |GL(3, F₂)|         = 168   (Gl3.agda, MetricGauge documentation)
--   |orbit(metric-id)|  = 28    (3 exemplars witnessed; full
--                                  characterisation deferred)
--   |stabiliser|        = 6     (Coxeter S₃; 3 of 6 elements now
--                                  witnessed: s₁, s₂, s₁∘Ls₂)
--
--   28 · 6 = 168 ✓   (orbit-stabiliser theorem instance)
--
-- The Coxeter (s₁ s₂)³ = e relation now has structural content:
-- applying the 3-cycle three times returns to identity, which would
-- be a derived consequence of stabiliser-closure-full. This slice
-- shows the 3-cycle stabilises; iterating it (which preserves the
-- stabilisation) is implicit but not formally proven here.
--
-- Deferred coalgebraic-unfolding slices:
--
--   * **stabiliser-closure-full**: prove s₂∘Ls₁ and s₁∘Ls₂∘Ls₁ also
--     stabilise metric-id. Each follows the same template as this
--     slice. ~150 LoC. Closes the full 6-element stabiliser group.
--
--   * **congruence-compose**: the general algebraic lemma
--     `congruence-act T₂ (congruence-act T₁ M) ≡ congruence-act
--     (T₁ ∘L T₂) M`. Implies stabiliser-closure for ANY composition
--     of stabilising elements (= the stabiliser is a subgroup of
--     GL(3, F₂)). Requires bilinearity infrastructure (~200 LoC) +
--     pullback + compose (~100 LoC). ~300 LoC total.
--
--   * **bridge-to-Substrate.Groups.S3**: formally connect this
--     concrete Linear 3 3 stabiliser to the existing S₃ group
--     structure in Substrate.Groups.S3.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- N-4: Categorical retrofit — 3-cycle stabilisation as FixedPoint.
--
-- Per `feedback_categorical_name_first` and the
-- Substrate.Category.Primitives roadmap. With `congruence-compose`
-- eventually formalised (deferred), this witness becomes derivable as
-- `FixedPoint-of-compose metric-id-fixed-by-cong-act-s₁
--                        metric-id-fixed-by-cong-act-s₂` modulo the
-- composition law `congruence-act (s₁ ∘L s₂) ≡
-- congruence-act s₁ ∘E congruence-act s₂`. Until then, the explicit
-- wrapper documents the categorical handle without losing the
-- per-cycle proof's content.
------------------------------------------------------------------------

metric-id-fixed-by-cong-act-s₁∘s₂ :
  FixedPoint (congruence-act (s₁ ∘L s₂)) metric-id
metric-id-fixed-by-cong-act-s₁∘s₂ =
  record { fixed = s₁∘s₂-stabilises-metric-id }
