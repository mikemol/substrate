------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-F2Graded-CountA
--
-- V₄'s second F₂-grading: count of A generators, mod 2. Thin instance
-- of FromCoxeterHomomorphism over `count-by sel-A`.
--
-- Splits V₄ as {ε, B} (degree 𝟘) vs {A, AB} (degree 𝟙).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Coxeter-F2Graded-CountA where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (refl)

import Substrate.Groups.V4-Coxeter as V₄
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)
open import Substrate.Groups.Coxeter.Word.Count using (count-by; count-by-distrib)

sel-A : V₄.Gen → ℕ
sel-A V₄.A = suc zero
sel-A V₄.B = zero

count-A = count-by sel-A
count-A-distrib = count-by-distrib sel-A

------------------------------------------------------------------------
-- V₄ as F₂-graded via count-A-parity (via the combinator).
------------------------------------------------------------------------

open import Substrate.Category.RGradedMonoid.FromCoxeterHomomorphism
  (Word V₄.Gen)
  _++_
  []
  (λ a b c → V₄.++-assoc a b c)
  ++-identity-left
  ++-identity-right
  count-A
  refl
  count-A-distrib
  public
  renaming (F₂Graded-from-Homomorphism to V4-F2Graded-CountA)
