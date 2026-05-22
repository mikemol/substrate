------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-F2Graded-CountA
--
-- V₄'s second F₂-grading: count of A generators, mod 2. Thin instance
-- of Substrate.Groups.V4-Coxeter-F2GradedFromHomomorphism over
-- `count-by sel-A`.
--
-- Splits V₄ as {ε, B} (degree 𝟘) vs {A, AB} (degree 𝟙).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Coxeter-F2Graded-CountA where

open import Substrate.Foundation.Nat using (zero; suc)
open import Substrate.Foundation.Eq using (refl)

import Substrate.Groups.V4-Coxeter as V₄
open import Substrate.Groups.Coxeter.Word.Count using (count-by; count-by-distrib)

sel-A : V₄.Gen → _
sel-A V₄.A = suc zero
sel-A V₄.B = zero

open import Substrate.Groups.V4-Coxeter-F2GradedFromHomomorphism
  (count-by sel-A) refl (count-by-distrib sel-A)
  public
  renaming (F₂Graded-from-Homomorphism to V4-F2Graded-CountA)
