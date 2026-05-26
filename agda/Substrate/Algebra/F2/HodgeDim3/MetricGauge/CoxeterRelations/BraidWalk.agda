------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidWalk
--
-- Generic Coxeter braid-walk witness: given 6 step-equations
-- expressing two 3-step walks meeting at a common point, produce
--   apply (s₁ ∘L s₂ ∘L s₁) a₀ ≡ apply (s₂ ∘L s₁ ∘L s₂) a₀.
--
-- LHS walk:   a₀ →s₁→ a₁ →s₂→ a₂ →s₁→ m
-- RHS walk:   a₀ →s₂→ b₁ →s₁→ b₂ →s₂→ m
--
-- The 6-step trans-chain in the body (3 forward + 3 sym-backward,
-- joined at meet-point m) is the SHAPE that the per-starting-basis
-- files (BraidOnE0/E1/E2) all share; this module names that shape.
-- Per-starting-basis files reduce to a one-line call.
--
-- Companion to CubedOrbitWalk and SquaredOrbitWalk: where the cubed
-- walk handles (s₁∘s₂)³ and the squared walk handles s², the braid
-- walk handles the braid relation s₁s₂s₁ = s₂s₁s₂ that defines S₃ as
-- a Coxeter group on two involution generators.
--
-- `a₀` is explicit (consistent with CubedOrbitWalk + SquaredOrbitWalk)
-- to avoid unification deadlock when s₁/s₂ are built via
-- linear-from-images and basis vectors don't reduce mechanically.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidWalk where

open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (Linear; apply; _∘L_)

------------------------------------------------------------------------
-- The 6-step trans/cong/sym chain underlying s₁s₂s₁ ≡ s₂s₁s₂ on any
-- starting vector. The 6 step-equations witness the two walks
--   a₀ →s₁→ a₁ →s₂→ a₂ →s₁→ m   (LHS, all forward)
--   a₀ →s₂→ b₁ →s₁→ b₂ →s₂→ m   (RHS, applied in sym below)
-- meeting at the common point m.
------------------------------------------------------------------------

braid-walk :
  ∀ {n} (s₁ s₂ : Linear n n) (a₀ : Vector n)
  {a₁ a₂ b₁ b₂ m : Vector n} →
  apply s₁ a₀ ≡ a₁ →
  apply s₂ a₁ ≡ a₂ →
  apply s₁ a₂ ≡ m  →
  apply s₂ b₂ ≡ m  →
  apply s₁ b₁ ≡ b₂ →
  apply s₂ a₀ ≡ b₁ →
  apply (s₁ ∘L s₂ ∘L s₁) a₀ ≡ apply (s₂ ∘L s₁ ∘L s₂) a₀
braid-walk s₁ s₂ _ e1 e2 e3 e4 e5 e6 =
  trans (cong (apply s₁) (cong (apply s₂) e1))
  (trans (cong (apply s₁) e2)
  (trans e3
  (trans (sym e4)
  (trans (cong (apply s₂) (sym e5))
         (cong (apply s₂) (cong (apply s₁) (sym e6)))))))
