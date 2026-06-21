------------------------------------------------------------------------
-- Substrate.Algebra.CayleyDickson.Curve
--
-- ⊙.c8 — the Morton / Hilbert curve-crossover, as a tropical (cost) instance.
-- The loosest commuting-sphere conjecture (#8, a framing): a space-filling curve
-- linearizes the F₂ⁿ index; Morton (Z-order) is the plain index rank, Hilbert is
-- a locality-preserving reordering, and WHICH to use crosses over at a grade
-- boundary CHOSEN BY THE COST (tropical) instance.
--
-- This grounds the framing without reinventing a curve (none exists in the tree):
--   * `morton` is the Z-order linearization (index → rank), reusing `Grade.bit`;
--   * the crossover IS the tropical min ⊓ (NatInf — the same cost gauge ⊙.c6's
--     Contraction reads): of two curves' costs, take the cheaper; the chosen curve
--     is the argmin, and the crossover BOUNDARY is the grade where the argmin flips.
-- The full Hilbert construction (the recursive quadrant reflection) is a separate
-- build; only the SELECTION mechanism — a tropical argmin — is C8's content.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Algebra.Semiring.NatInf using (ℕ∞; fin; ∞; _⊓_)
open import Substrate.Algebra.CayleyDickson.Grade using (bit)

------------------------------------------------------------------------
-- 1. The Morton / Z-order linearization: the F₂ⁿ index → its rank (LSB-first
--    binary value Σ bitᵢ·2ⁱ, written as repeated doubling so no * is needed).
--    Traversing indices in increasing `morton` rank IS the Morton curve.
------------------------------------------------------------------------

morton : {n : ℕ} → Vec Bool n → ℕ
morton []       = zero
morton (b ∷ bs) = bit b + (morton bs + morton bs)

-- e.g. the index 1·2⁰ + 0·2¹ + 1·2² has Morton rank 5.
_ : morton (true ∷ false ∷ true ∷ []) ≡ 5
_ = refl

------------------------------------------------------------------------
-- 2. The crossover is a TROPICAL (min-cost) selection. Of two curves' costs the
--    crossover takes the cheaper — exactly the tropical ⊕ = ⊓ on ℕ∞. The chosen
--    curve at a grade is the argmin; the crossover boundary is where it flips.
------------------------------------------------------------------------

crossover : ℕ∞ → ℕ∞ → ℕ∞
crossover = _⊓_

-- Model: Morton's jump-cost doubles per grade (Z-order leaps across quadrant
-- boundaries), while Hilbert's locality cost grows slowly. At a low grade Morton
-- is cheaper; at a high grade Hilbert wins — the argmin (hence the curve) flips.
crossover-low  : crossover (fin 2) (fin 4) ≡ fin 2   -- low grade  → Morton (Z-order) cheaper
crossover-low  = refl

crossover-high : crossover (fin 8) (fin 6) ≡ fin 6   -- high grade → Hilbert (locality) wins
crossover-high = refl

-- ∞ (unreachable) is the cost identity: a curve with no cost never wins a crossover.
crossover-∞ʳ : crossover (fin 3) ∞ ≡ fin 3
crossover-∞ʳ = refl
