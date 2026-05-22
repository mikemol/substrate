------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-F2Graded-CountB
--
-- V₄'s third F₂-grading: count of B generators, mod 2. Thin instance
-- of FromCoxeterHomomorphism over `count-by sel-B`.
--
-- Splits V₄ as {ε, A} (degree 𝟘) vs {B, AB} (degree 𝟙). Together
-- with length-parity and count-A-parity, gives the V₄ ≅ Z/2 × Z/2
-- coordinate iso.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Coxeter-F2Graded-CountB where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (refl)

import Substrate.Groups.V4-Coxeter as V₄
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)
open import Substrate.Groups.Coxeter.Word.Count using (count-by; count-by-distrib)

sel-B : V₄.Gen → ℕ
sel-B V₄.A = zero
sel-B V₄.B = suc zero

count-B = count-by sel-B
count-B-distrib = count-by-distrib sel-B

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
