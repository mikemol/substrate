------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Utilities.Degree
--
-- degree: Maybe-ℕ representation of polynomial degree.
--   nothing for the zero polynomial (degree -∞ convention);
--   just k for a nonzero polynomial whose leading position is k.
-- Alias for leading-position; presented under the more semantically
-- transparent name for comparison and arithmetic contexts.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Utilities.Degree where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Maybe using (Maybe)

open import Substrate.Algebra.F2.Polynomial using (Polynomial)
open import Substrate.Algebra.F2.Polynomial.Utilities.LeadingPosition
  using (leading-position)

degree : ∀ {n} → Polynomial n → Maybe ℕ
degree = leading-position
