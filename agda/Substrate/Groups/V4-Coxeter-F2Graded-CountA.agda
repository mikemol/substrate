------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-F2Graded-CountA
--
-- V₄'s second F₂-grading: count of A generators, mod 2.
-- Refactored via the FromCoxeterHomomorphism combinator.
--
-- Splits V₄ as {ε, B} (degree 𝟘) vs {A, AB} (degree 𝟙).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Coxeter-F2Graded-CountA where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

import Substrate.Groups.V4-Coxeter as V₄
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _∷_; _++_; ++-identity-left; ++-identity-right)

------------------------------------------------------------------------
-- count-A — count of A generators (the ℕ-homomorphism).
------------------------------------------------------------------------

count-A : Word V₄.Gen → ℕ
count-A []          = zero
count-A (V₄.A ∷ w)  = suc (count-A w)
count-A (V₄.B ∷ w)  = count-A w

count-A-distrib :
  (a b : Word V₄.Gen) →
  count-A (a ++ b) ≡ count-A a + count-A b
count-A-distrib []          b = refl
count-A-distrib (V₄.A ∷ a)  b = cong suc (count-A-distrib a b)
count-A-distrib (V₄.B ∷ a)  b = count-A-distrib a b

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
