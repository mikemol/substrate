------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-F2GradedFromHomomorphism
--
-- Parametric shim: takes a ℕ-homomorphism on Word V₄.Gen-V4 and applies
-- the generic Substrate.Category.RGradedMonoid.FromCoxeterHomomorphism
-- combinator with V₄'s fixed Word / _++_ / ε / identity / associativity.
--
-- Factors out the V₄-specific boilerplate that
-- V4-Coxeter-F2Graded.agda (length), -F2Graded-CountA (count-by sel-A),
-- and -F2Graded-CountB (count-by sel-B) all repeat. Each thin instance
-- now supplies just the homomorphism ℕ+ its ε-vanishing ℕ+ its distrib
-- lemma.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus

import Substrate.Groups.V4-Coxeter as V₄
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

open import Substrate.Foundation.Eq
module Substrate.Groups.V4-Coxeter-F2GradedFromHomomorphism
  (hom         : Word V₄.Gen-V4 → ℕ)
  (hom-ε       : hom [] ≡ zero)
  (hom-distrib : (a b : Word V₄.Gen-V4) → hom (a ++ b) ≡ hom a ℕ+ hom b)
  where


