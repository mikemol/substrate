------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.CubedOrbitWalk
--
-- Generic (s₁ ∘L s₂)³ orbit-walk witness: given 6 step-equations
-- following the (s₂, s₁, s₂, s₁, s₂, s₁) alternation, produce the
-- cubed-Coxeter equation
--   apply ((s₁ ∘L s₂) ∘L (s₁ ∘L s₂) ∘L (s₁ ∘L s₂)) a₀ ≡ a₆.
--
-- The 5-call cong-trans chain in the body is the SHAPE that the per-
-- starting-basis files (S1S2CubedOnE0/E1/E2) all share; this module
-- names that shape and takes the orbit's 6 lemma references as
-- parameters. Per-starting-basis files reduce to a one-line call.
--
-- Surfaced by typed-holes on S1S2CubedOnE0 ↔ S1S2CubedOnE1 (9 shared
-- lines / 18 code lines) after the cong-trans arc closed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.CubedOrbitWalk where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; cong; cong-trans)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (Linear; apply; _∘L_)

------------------------------------------------------------------------
-- The 5-step cong-trans chain underlying (s₁ ∘L s₂)³ on any starting
-- basis element. The 6 step-equations witness the orbit walk
--   a₀ →s₂→ a₁ →s₁→ a₂ →s₂→ a₃ →s₁→ a₄ →s₂→ a₅ →s₁→ a₆.
------------------------------------------------------------------------

cubed-orbit-walk :
  ∀ {n} (s₁ s₂ : Linear n n) (a₀ : Vector n) {a₁ a₂ a₃ a₄ a₅ a₆ : Vector n} →
  apply s₂ a₀ ≡ a₁ →
  apply s₁ a₁ ≡ a₂ →
  apply s₂ a₂ ≡ a₃ →
  apply s₁ a₃ ≡ a₄ →
  apply s₂ a₄ ≡ a₅ →
  apply s₁ a₅ ≡ a₆ →
  apply ((s₁ ∘L s₂) ∘L (s₁ ∘L s₂) ∘L (s₁ ∘L s₂)) a₀ ≡ a₆
cubed-orbit-walk s₁ s₂ _ e₁ e₂ e₃ e₄ e₅ e₆ =
  cong-trans (apply (s₁ ∘L s₂)) (cong (apply (s₁ ∘L s₂)) (cong (apply s₁) e₁))
  (cong-trans (apply (s₁ ∘L s₂)) (cong (apply (s₁ ∘L s₂)) e₂)
  (cong-trans (apply (s₁ ∘L s₂)) (cong (apply s₁) e₃)
  (cong-trans (apply (s₁ ∘L s₂)) e₄
  (cong-trans (apply s₁) e₅
         e₆))))
