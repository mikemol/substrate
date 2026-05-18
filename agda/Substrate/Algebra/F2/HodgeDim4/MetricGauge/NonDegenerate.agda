------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.MetricGauge.NonDegenerate
--
-- M-11.metric-gauge.metric-id-4-non-degenerate slice. First non-trivial
-- property of the dim-4 foundation: `metric-id-4 ∈ NonDegenerate-4`,
-- via the kernel-free predicate.
--
-- Argument: if v pairs to 𝟘 with every w, then in particular pairing
-- with each basis vector eᵢ gives vᵢ ≡ 𝟘. With v₀ = v₁ = v₂ = v₃ = 𝟘,
-- v ≡ 𝟎ⱽ by `≡-from-lookup`.
--
-- The 4 per-basis pairing lemmas reduce `bilinear-form-of-4 metric-id-4
-- v eᵢ` to vᵢ. After Agda's pattern reductions on `_·_` and `_+_` (both
-- pivot on first arg), the LHS for w = e₀ stabilises at
-- `((v₀·𝟙 + v₁·𝟘) + v₂·𝟘) + v₃·𝟘` — neither term reduces further
-- because the leftmost factor (vᵢ) is a variable, not a constructor.
-- Each lemma chains `·-absorbʳ` (kills off-diagonal vⱼ·𝟘 terms) and
-- `+-identity{ˡ,ʳ}` (collapses the resulting +𝟘's) to reach vᵢ.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.MetricGauge.NonDegenerate where

open import Data.Fin using (Fin; zero; suc)
open import Data.Vec using (Vec; []; _∷_; lookup)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.HodgeDim4.MetricGauge

------------------------------------------------------------------------
-- N-1: Per-basis pairing lemmas.
--
-- bilinear-form-of-4 metric-id-4 v eᵢ ≡ vᵢ for each basis vector eᵢ.
--
-- For e₀ = (𝟙∷𝟘∷𝟘∷𝟘∷[]):
--   bilinear-form-of-4 metric-id-4 (v₀∷v₁∷v₂∷v₃∷[]) e₀
--   reduces (by Agda's first-arg pivot on `_·_` and `_+_`) to:
--     ((v₀·𝟙 + v₁·𝟘) + v₂·𝟘) + v₃·𝟘
--   Need to reach v₀. Chain:
--     ↦ ((v₀·𝟙 + v₁·𝟘) + v₂·𝟘) + 𝟘    [·-absorbʳ v₃]
--     ↦ (v₀·𝟙 + v₁·𝟘) + v₂·𝟘            [+-identityʳ]
--     ↦ (v₀·𝟙 + v₁·𝟘) + 𝟘               [·-absorbʳ v₂]
--     ↦ v₀·𝟙 + v₁·𝟘                      [+-identityʳ]
--     ↦ v₀·𝟙 + 𝟘                         [·-absorbʳ v₁]
--     ↦ v₀·𝟙                             [+-identityʳ]
--     ↦ v₀                               [·-identityʳ]
------------------------------------------------------------------------

pair-metric-id-4-with-e₀ :
  (v : Vector 4) →
  bilinear-form-of-4 metric-id-4 v (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) ≡ lookup v zero
pair-metric-id-4-with-e₀ (v₀ ∷ v₁ ∷ v₂ ∷ v₃ ∷ []) =
  trans (cong (((v₀ · 𝟙 + v₁ · 𝟘) + v₂ · 𝟘) +_) (·-absorbʳ v₃))
  (trans (+-identityʳ ((v₀ · 𝟙 + v₁ · 𝟘) + v₂ · 𝟘))
  (trans (cong ((v₀ · 𝟙 + v₁ · 𝟘) +_) (·-absorbʳ v₂))
  (trans (+-identityʳ (v₀ · 𝟙 + v₁ · 𝟘))
  (trans (cong (v₀ · 𝟙 +_) (·-absorbʳ v₁))
  (trans (+-identityʳ (v₀ · 𝟙))
         (·-identityʳ v₀))))))

-- For e₁ = (𝟘∷𝟙∷𝟘∷𝟘∷[]):
--   LHS reduces to ((v₀·𝟘 + v₁·𝟙) + v₂·𝟘) + v₃·𝟘. Goal: v₁.
--   Chain: kill v₃·𝟘, then v₂·𝟘, then v₀·𝟘 (leftmost — needs +-identityˡ
--   after absorption), then v₁·𝟙 → v₁.
pair-metric-id-4-with-e₁ :
  (v : Vector 4) →
  bilinear-form-of-4 metric-id-4 v (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) ≡ lookup v (suc zero)
pair-metric-id-4-with-e₁ (v₀ ∷ v₁ ∷ v₂ ∷ v₃ ∷ []) =
  trans (cong (((v₀ · 𝟘 + v₁ · 𝟙) + v₂ · 𝟘) +_) (·-absorbʳ v₃))
  (trans (+-identityʳ ((v₀ · 𝟘 + v₁ · 𝟙) + v₂ · 𝟘))
  (trans (cong ((v₀ · 𝟘 + v₁ · 𝟙) +_) (·-absorbʳ v₂))
  (trans (+-identityʳ (v₀ · 𝟘 + v₁ · 𝟙))
  (trans (cong (_+ v₁ · 𝟙) (·-absorbʳ v₀))
  (trans (+-identityˡ (v₁ · 𝟙))
         (·-identityʳ v₁))))))

-- For e₂ = (𝟘∷𝟘∷𝟙∷𝟘∷[]):
--   LHS reduces to ((v₀·𝟘 + v₁·𝟘) + v₂·𝟙) + v₃·𝟘. Goal: v₂.
pair-metric-id-4-with-e₂ :
  (v : Vector 4) →
  bilinear-form-of-4 metric-id-4 v (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []) ≡ lookup v (suc (suc zero))
pair-metric-id-4-with-e₂ (v₀ ∷ v₁ ∷ v₂ ∷ v₃ ∷ []) =
  trans (cong (((v₀ · 𝟘 + v₁ · 𝟘) + v₂ · 𝟙) +_) (·-absorbʳ v₃))
  (trans (+-identityʳ ((v₀ · 𝟘 + v₁ · 𝟘) + v₂ · 𝟙))
  (trans (cong (_+ v₂ · 𝟙) (cong (_+ v₁ · 𝟘) (·-absorbʳ v₀)))
  (trans (cong (_+ v₂ · 𝟙) (+-identityˡ (v₁ · 𝟘)))
  (trans (cong (_+ v₂ · 𝟙) (·-absorbʳ v₁))
  (trans (+-identityˡ (v₂ · 𝟙))
         (·-identityʳ v₂))))))

-- For e₃ = (𝟘∷𝟘∷𝟘∷𝟙∷[]):
--   LHS reduces to ((v₀·𝟘 + v₁·𝟘) + v₂·𝟘) + v₃·𝟙. Goal: v₃.
pair-metric-id-4-with-e₃ :
  (v : Vector 4) →
  bilinear-form-of-4 metric-id-4 v (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []) ≡ lookup v (suc (suc (suc zero)))
pair-metric-id-4-with-e₃ (v₀ ∷ v₁ ∷ v₂ ∷ v₃ ∷ []) =
  trans (cong (_+ v₃ · 𝟙) (cong (_+ v₂ · 𝟘) (cong (_+ v₁ · 𝟘) (·-absorbʳ v₀))))
  (trans (cong (_+ v₃ · 𝟙) (cong (_+ v₂ · 𝟘) (+-identityˡ (v₁ · 𝟘))))
  (trans (cong (_+ v₃ · 𝟙) (cong (_+ v₂ · 𝟘) (·-absorbʳ v₁)))
  (trans (cong (_+ v₃ · 𝟙) (+-identityˡ (v₂ · 𝟘)))
  (trans (cong (_+ v₃ · 𝟙) (·-absorbʳ v₂))
  (trans (+-identityˡ (v₃ · 𝟙))
         (·-identityʳ v₃))))))

------------------------------------------------------------------------
-- N-2: metric-id-4 ∈ NonDegenerate-4.
--
-- Direct application of N-1 four times: given the hypothesis that
-- bilinear-form-of-4 metric-id-4 v w ≡ 𝟘 for ALL w, specialise to
-- w = eᵢ for i = 0, 1, 2, 3 to extract vᵢ ≡ 𝟘 at each position.
-- Conclude v ≡ 𝟎ⱽ via ≡-from-lookup.
------------------------------------------------------------------------

metric-id-4-non-degenerate : NonDegenerate-4 metric-id-4
metric-id-4-non-degenerate v hyp = ≡-from-lookup v 𝟎ⱽ goal
  where
    -- lookup (𝟎ⱽ {4}) i ≡ 𝟘 by computation (𝟎ⱽ = replicate 4 𝟘); no
    -- explicit lookup-𝟎 bridge needed.
    goal : (i : Fin 4) → lookup v i ≡ lookup (𝟎ⱽ {4}) i
    goal zero =
      trans (sym (pair-metric-id-4-with-e₀ v))
            (hyp (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []))
    goal (suc zero) =
      trans (sym (pair-metric-id-4-with-e₁ v))
            (hyp (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []))
    goal (suc (suc zero)) =
      trans (sym (pair-metric-id-4-with-e₂ v))
            (hyp (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []))
    goal (suc (suc (suc zero))) =
      trans (sym (pair-metric-id-4-with-e₃ v))
            (hyp (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []))

------------------------------------------------------------------------
-- N-3: Capstone documentation.
--
-- The dim-4 diagonal identity metric is non-degenerate. This
-- inhabits the type `Σ SymBilinForm-4 NonDegenerate-4` with the
-- canonical witness, anchoring the GL(4, F₂) orbit at a concrete
-- non-degenerate form (just as `metric-id` does at dim 3).
--
-- The argument pattern (pair with each eᵢ; extract vᵢ; conclude
-- v ≡ 𝟎ⱽ via componentwise extensionality) is the **universal-
-- property template for kernel-free non-degeneracy at any dim n**.
-- The 4 N-1 lemmas are the n=4 instances of a generic
-- "pair-diagonal-with-basis" pattern.
--
-- The proof template's shape — 6-step chain of `·-absorbʳ` +
-- `+-identity{ˡ,ʳ}` collapsing the off-diagonal v's — is identical
-- across the 4 N-1 lemmas modulo which index is the "live" one. A
-- combinator that captures the pattern parametrically (over the live
-- index) is a coalgebraic-unfolding follow-on; explicit per-basis
-- lemmas suffice here because n=4 is small.
--
-- Deferred coalgebraic-unfolding slices:
--
--   * Generalise `pair-diagonal-with-basis` to a generic combinator
--     over (n, diagonal-vector). Would let `metric-id-n-non-degenerate`
--     follow as the all-ones-diagonal instance, applicable at any n.
--
--   * `metric-mixed-4-non-degenerate` and other exemplar non-degeneracy
--     witnesses (each follows the kernel-free pattern; specific
--     algebra differs by off-diagonal coupling).
--
--   * `HodgeRecast-4` (= `_·F_ v w ≡ bilinear-form-of-4 metric-id-4 v w`).
--     Together with this slice, would establish that the implicit
--     dot-product non-degeneracy at dim 4 is the metric-id-4 instance.
------------------------------------------------------------------------
