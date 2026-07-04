{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.CFDigitHet — ⟡N1b-Real-digit, via HetQ (operator:
-- "See again, HetQ").
--
-- THE DISSOLVED TENSION: I worried the generator→digit map must produce
-- REGULAR CF digits (ℕ, ≥1) to fit RealTrace/convergent — but interned ids
-- aren't ≥1. That presupposes SQUASHING the generator into ℕ. HetQ says don't:
-- HetQ A B has num ∈ A, den ∈ B for ARBITRARY A, B — no ℕ, no ≥1 constraint
-- (⟡H0: HetBasis.HetQ record + CrossEq are generic in A/B; the ≥1/AllPos
-- regularity is specific to RealTrace, NOT to the het-CF framework).
--
-- So the "digit" is the GENERATOR ITSELF (carrier A); comparison is the
-- cross-equality _≈H_ into a common carrier R via viaBridges (a codec per
-- carrier). FAITHFULNESS (distinct periods → distinct reals = correction #7
-- lens-soundness at CF tier) is then INTRINSIC: it IS the cross-equality, and
-- interning identity is the equality on A. The lens need not be injective-into-
-- ℕ; it is the identity on the generator carrier, compared via CrossMul.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.CFDigitHet where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Q.HetBasis using (HetQ; _//_; hnum; hden; module CrossEq; viaBridges)

------------------------------------------------------------------------
-- The regress "digit" carrier is the GENERATOR carrier A (arbitrary). A
-- convergent/CF-value of a regress lives in HetQ A B — generator numerator,
-- denominator in B. No ℕ, no ≥1. The cross-multiply into a common R is built
-- from a codec per carrier (viaBridges): codecA : A → R is the generator's
-- fingerprint into R — NOT required injective, NOT required ≥1.
------------------------------------------------------------------------
module GenDigit
  (A B R : Set)
  (codecA : A → R) (codecB : B → R)
  (_·R_ : R → R → R)
  (_≈R_ : R → R → Set)
  (≈R-refl : ∀ {x} → x ≈R x)
  (≈R-sym  : ∀ {x y} → x ≈R y → y ≈R x)
  where

  -- the cross-multiply: the generator-digit and the denominator meet in R.
  _⊗_ : A → B → R
  _⊗_ = viaBridges codecA codecB _·R_

  open CrossEq _⊗_ _≈R_ ≈R-refl ≈R-sym public   -- _≈H_, ≈H-refl, ≈H-sym

  -- a regress value = a HetQ A B (generator numerator, no squashing).
  RegressValue : Set
  RegressValue = HetQ A B

  -- FAITHFULNESS is the cross-equality: two regress values are equal EXACTLY
  -- when their cross-terms agree in R. distinct-in-R ⟹ distinct values. This
  -- is correction #7 at the CF tier: the lens (codecA) feeds the cross-term;
  -- equality is representation-INDEPENDENT (the ≥1 regularity never enters).
  faithful-is-crosseq :
    (p q : RegressValue) →
    p ≈H q ≡ ((hnum p ⊗ hden q) ≈R (hnum q ⊗ hden p))
  faithful-is-crosseq p q = refl

  -- and the cross-term IS the codec pair (viaBridges), refl: the generator's
  -- fingerprint codecA and the denominator's codecB, multiplied in R. The lens
  -- is codecA; it need not land in ℕ≥1 — R is arbitrary.
  crossterm-is-codecs :
    (a : A) (b : B) → (a ⊗ b) ≡ (codecA a ·R codecB b)
  crossterm-is-codecs a b = refl
