------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-F2GradedFromHomomorphism
--
-- Parametric shim: takes a ℕ-homomorphism on Word V₄.Gen and applies
-- the generic Substrate.Category.RGradedMonoid.FromCoxeterHomomorphism
-- combinator with V₄'s fixed Word / _++_ / ε / identity / associativity.
--
-- Factors out the V₄-specific boilerplate that
-- V4-Coxeter-F2Graded.agda (length), -F2Graded-CountA (count-by sel-A),
-- and -F2Graded-CountB (count-by sel-B) all repeat. Each thin instance
-- now supplies just the homomorphism + its ε-vanishing + its distrib
-- lemma.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; zero; _+_)
open import Substrate.Foundation.Eq using (_≡_)

import Substrate.Groups.V4-Coxeter as V₄
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

module Substrate.Groups.V4-Coxeter-F2GradedFromHomomorphism
  (hom         : Word V₄.Gen → ℕ)
  (hom-ε       : hom [] ≡ zero)
  (hom-distrib : (a b : Word V₄.Gen) → hom (a ++ b) ≡ hom a + hom b)
  where

open import Substrate.Category.RGradedMonoid.FromCoxeterHomomorphism
  (Word V₄.Gen)
  _++_
  []
  (λ a b c → V₄.++-assoc a b c)
  ++-identity-left
  ++-identity-right
  hom
  hom-ε
  hom-distrib
  public
