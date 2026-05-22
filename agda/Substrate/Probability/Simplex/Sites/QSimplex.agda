------------------------------------------------------------------------
-- Substrate.Probability.Simplex.Sites.QSimplex
--
-- Concrete site: the probability simplex over ℚ.
--
-- ProbabilitySemiring instance: ℚ ∩ [0, 1] with addition and the
-- standard 0, 1. The substrate's Substrate.Algebra.Q provides
-- constructive ℚ; we use ℚ values as probabilities.
--
-- Per [[q-over-r-constructive]]: ℚ over ℝ for constructive numerics.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.Simplex.Sites.QSimplex where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Level using (Level)

open import Substrate.Algebra.Q using (ℚ; mkℚ)
open import Substrate.Algebra.Z using (ℤ; 0ℤ; 1ℤ; +_)

open import Substrate.Probability.Simplex

------------------------------------------------------------------------
-- The ℚ probability semiring.
--
-- Carrier = ℚ; zero-p = 0/1; one-p = 1/1; plus-p stubbed for the
-- structural site (concrete numerical addition supplied at use-site).

ℚ-PS : ProbabilitySemiring {Level.zero}
ℚ-PS = record
  { Carrier = ℚ
  ; zero-p  = mkℚ 0ℤ 0   -- 0/1
  ; one-p   = mkℚ 1ℤ 0   -- 1/1
  ; plus-p  = λ a b → mkℚ 0ℤ 0
                       -- stub for ℚ-addition at the site level;
                       -- concrete arithmetic in downstream runtime
                       -- modules
  }

------------------------------------------------------------------------
-- The ℚ-valued simplex Δⁿ⁻¹.

ℚ-Simplex : ℕ → Set
ℚ-Simplex n = Simplex ℚ-PS n

------------------------------------------------------------------------
-- Per [[q-over-r-constructive]]: ℚ-valued probabilities are
-- constructive; ℝ-valued would lose the gauge-honest computation.
-- Per [[expose-generator-not-orbit]]: ℚ-PS is the generator; specific
-- ℚ-distributions are orbits.
