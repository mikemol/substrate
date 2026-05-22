------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-F2Graded-CountB
--
-- V₄'s third F₂-grading: count of B generators, mod 2. Thin instance
-- of Substrate.Groups.V4-Coxeter-F2GradedFromHomomorphism over
-- `count-by sel-B`.
--
-- Splits V₄ as {ε, A} (degree 𝟘) vs {B, AB} (degree 𝟙). Together
-- with length-parity and count-A-parity, gives the V₄ ≅ Z/2 × Z/2
-- coordinate iso.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Coxeter-F2Graded-CountB where

open import Substrate.Foundation.Nat using (zero; suc)
open import Substrate.Foundation.Eq using (refl)

import Substrate.Groups.V4-Coxeter as V₄
open import Substrate.Groups.Coxeter.Word.Count using (count-by; count-by-distrib)

sel-B : V₄.Gen → _
sel-B V₄.A = zero
sel-B V₄.B = suc zero

open import Substrate.Groups.V4-Coxeter-F2GradedFromHomomorphism
  (count-by sel-B) refl (count-by-distrib sel-B)
  public
  renaming (F₂Graded-from-Homomorphism to V4-F2Graded-CountB)
