------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.SquaredOrbitWalk
--
-- Generic involution-step / squared-orbit witness: given two step-
-- equations following the orbit a₀ →s→ a₁ →s→ a₂, produce
--   apply (s ∘L s) a₀ ≡ a₂.
--
-- The single-step `trans (cong (apply s) <first>) <second>` is the
-- SHAPE that the per-starting-basis files (S{1,2}SquaredOn{E0,E1,E2})
-- all share; this module names that shape and takes the orbit's two
-- lemma references as parameters. Per-starting-basis files reduce to
-- a one-line call.
--
-- Companion to CubedOrbitWalk: where the cubed walk handles the
-- (s₁ ∘L s₂)³ orbit, the squared walk handles the s² involution.
-- Together they cover the 6+6 = 12 Coxeter-relation cells in the
-- MetricGauge/CoxeterRelations directory.
--
-- `a₀` is explicit (consistent with CubedOrbitWalk) to avoid
-- unification deadlock when `s` is built via linear-from-images and
-- the basis vectors don't reduce mechanically.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.SquaredOrbitWalk where

open import Substrate.Foundation.Eq using (_≡_; trans; cong)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (Linear; apply; _∘L_)

------------------------------------------------------------------------
-- The 1-step trans/cong chain underlying s ∘L s on any starting
-- vector. The 2 step-equations witness the orbit walk
--   a₀ →s→ a₁ →s→ a₂.
------------------------------------------------------------------------

squared-orbit-walk :
  ∀ {n} (s : Linear n n) (a₀ : Vector n) {a₁ a₂ : Vector n} →
  apply s a₀ ≡ a₁ →
  apply s a₁ ≡ a₂ →
  apply (s ∘L s) a₀ ≡ a₂
squared-orbit-walk s _ e₀ e₁ = trans (cong (apply s) e₀) e₁
