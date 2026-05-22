------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-F2Graded
--
-- V₄-Coxeter packaged as an F₂-graded monoid via length-parity.
--
-- Thin instance of Substrate.Groups.V4-Coxeter-F2GradedFromHomomorphism
-- applied to the length homomorphism. The grading splits V₄ as
-- {ε, AB} (degree 𝟘) vs {A, B} (degree 𝟙).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Coxeter-F2Graded where

open import Substrate.Foundation.Eq using (refl)
open import Substrate.Groups.Coxeter.Word.Length using (length; length-distrib)

open import Substrate.Groups.V4-Coxeter-F2GradedFromHomomorphism
  length refl length-distrib
  public
  renaming (F₂Graded-from-Homomorphism to V4-F2Graded)
