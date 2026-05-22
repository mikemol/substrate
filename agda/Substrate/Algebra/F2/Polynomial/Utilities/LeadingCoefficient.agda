------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Utilities.LeadingCoefficient
--
-- leading-coefficient: 𝟙 for nonzero polynomials (since at F₂ the
-- topmost nonzero coefficient is always 𝟙), 𝟘 for the zero
-- polynomial. This makes the function total.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Utilities.LeadingCoefficient where

open import Substrate.Foundation.Maybe using (Maybe; just; nothing)

open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.Algebra.F2.Polynomial using (Polynomial)
open import Substrate.Algebra.F2.Polynomial.Utilities.LeadingPosition
  using (leading-position)

leading-coefficient : ∀ {n} → Polynomial n → F₂
leading-coefficient p with leading-position p
... | nothing  = 𝟘
... | just _   = 𝟙
