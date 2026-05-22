------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.DegreeLt
--
-- degree-lt: comparison predicate over Maybe ℕ degrees.
-- nothing represents the zero polynomial (lowest "degree").
--   nothing  < nothing  = ⊥
--   nothing  < just _   = ⊤
--   just _   < nothing  = ⊥
--   just j   < just k   = j < k
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.DegreeLt where

open import Substrate.Foundation.Nat using (ℕ; _<_)
open import Substrate.Foundation.Maybe using (Maybe; nothing; just)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Unit using (⊤)

degree-lt : Maybe ℕ → Maybe ℕ → Set
degree-lt nothing  nothing  = ⊥
degree-lt nothing  (just _) = ⊤
degree-lt (just _) nothing  = ⊥
degree-lt (just j) (just k) = j < k
