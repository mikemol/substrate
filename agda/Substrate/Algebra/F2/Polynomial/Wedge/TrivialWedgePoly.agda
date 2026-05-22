------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.TrivialWedgePoly
--
-- Base case of polynomial long division: when p's degree is less
-- than q's (including p = 0), wedge is (quotient = 0, remainder = p).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.TrivialWedgePoly where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using ([])
open import Substrate.Algebra.F2.Polynomial using (Polynomial)
open import Substrate.Algebra.F2.Polynomial.Wedge.WedgePoly using (Wedge-Poly)

trivial-wedge-poly :
  ∀ {n m} (p : Polynomial n) (q : Polynomial m) →
  Wedge-Poly p q
trivial-wedge-poly {n} {m} p q = record
  { quotient-size  = 0
  ; quotient       = []
  ; remainder-size = n
  ; remainder      = p
  }
