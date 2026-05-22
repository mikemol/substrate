------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-F2Graded
--
-- V₄-Coxeter packaged as an F₂-graded monoid via length-parity, using
-- the FromCoxeterHomomorphism combinator.
--
-- Refactored from the prior hand-rolled version: now a one-line
-- application of the F₂-grading-from-homomorphism combinator, with
-- length being the canonical ℕ-homomorphism.
--
-- The grading splits V₄ as {ε, AB} (degree 𝟘) vs {A, B} (degree 𝟙).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Coxeter-F2Graded where

import Substrate.Groups.V4-Coxeter as V₄
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)
open import Substrate.Groups.Coxeter.Word.Length using (length; length-distrib)
open import Substrate.Foundation.Eq using (refl)

------------------------------------------------------------------------
-- V₄ as F₂-graded via length-parity (via the combinator).
------------------------------------------------------------------------

open import Substrate.Category.RGradedMonoid.FromCoxeterHomomorphism
  (Word V₄.Gen)
  _++_
  []
  (λ a b c → V₄.++-assoc a b c)
  ++-identity-left
  ++-identity-right
  length
  refl                          -- length [] ≡ 0 is refl
  length-distrib
  public
  renaming (F₂Graded-from-Homomorphism to V4-F2Graded)
