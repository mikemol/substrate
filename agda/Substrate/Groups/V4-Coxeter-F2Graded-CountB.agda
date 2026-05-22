------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-F2Graded-CountB
--
-- V₄'s third F₂-grading: count of B generators, mod 2.
-- Refactored via the FromCoxeterHomomorphism combinator.
--
-- Splits V₄ as {ε, A} (degree 𝟘) vs {B, AB} (degree 𝟙). Together
-- with length-parity and count-A-parity, gives the V₄ ≅ Z/2 × Z/2
-- coordinate iso.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Coxeter-F2Graded-CountB where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

import Substrate.Groups.V4-Coxeter as V₄
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _∷_; _++_; ++-identity-left; ++-identity-right)

------------------------------------------------------------------------
-- count-B — count of B generators (the ℕ-homomorphism).
------------------------------------------------------------------------

count-B : Word V₄.Gen → ℕ
count-B []          = zero
count-B (V₄.A ∷ w)  = count-B w
count-B (V₄.B ∷ w)  = suc (count-B w)

count-B-distrib :
  (a b : Word V₄.Gen) →
  count-B (a ++ b) ≡ count-B a + count-B b
count-B-distrib []          b = refl
count-B-distrib (V₄.A ∷ a)  b = count-B-distrib a b
count-B-distrib (V₄.B ∷ a)  b = cong suc (count-B-distrib a b)

------------------------------------------------------------------------
-- V₄ as F₂-graded via count-B-parity (via the combinator).
------------------------------------------------------------------------

open import Substrate.Category.RGradedMonoid.FromCoxeterHomomorphism
  (Word V₄.Gen)
  _++_
  []
  (λ a b c → V₄.++-assoc a b c)
  ++-identity-left
  ++-identity-right
  count-B
  refl
  count-B-distrib
  public
  renaming (F₂Graded-from-Homomorphism to V4-F2Graded-CountB)
