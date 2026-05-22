------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Utilities.LeadingPosition
--
-- leading-position: the topmost nonzero-coefficient position, or
-- nothing for the zero polynomial. Implemented via an accumulator
-- that tracks the highest-position-so-far seen.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Utilities.LeadingPosition where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Maybe using (Maybe; just; nothing)

open import Substrate.Algebra.F2 using (𝟘; 𝟙)
open import Substrate.Algebra.F2.Polynomial using (Polynomial)

leading-position-acc : ∀ {n} → Polynomial n → ℕ → Maybe ℕ → Maybe ℕ
leading-position-acc []        _   best = best
leading-position-acc (𝟘 ∷ p)   pos best = leading-position-acc p (suc pos) best
leading-position-acc (𝟙 ∷ p)   pos _    = leading-position-acc p (suc pos) (just pos)

leading-position : ∀ {n} → Polynomial n → Maybe ℕ
leading-position p = leading-position-acc p 0 nothing
