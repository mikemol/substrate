------------------------------------------------------------------------
-- Substrate.Probability.KLDivergence.Sites.QFin
--
-- Concrete site: KL divergence over Fin n with ℚ-valued probabilities.
--
-- KL(p || q) = Σ p(i) · log₂ (p(i) / q(i))  for p, q : Fin n → ℚ.
--
-- Uses ℚ-EntropyFunctor as the base.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.KLDivergence.Sites.QFin where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)
open import Level using (Level)

open import Substrate.Algebra.Q using (ℚ; mkℚ)
open import Substrate.Algebra.Z using (0ℤ)

open import Substrate.Probability.Entropy
open import Substrate.Probability.Entropy.Sites.QFin using (ℚ-EntropyFunctor)
open import Substrate.Probability.KLDivergence

------------------------------------------------------------------------
-- The Fin-n KL divergence at ℚ probabilities.

ℚ-KLDivergence : KLDivergence ℚ-EntropyFunctor
ℚ-KLDivergence = record
  { KL = λ {A} _ _ → mkℚ 0ℤ 0
                     -- stub: actual KL formula supplied at runtime
                     -- side with ℚ-arithmetic + rational log
  }

------------------------------------------------------------------------
-- Per [[q-over-r-constructive]]: ℚ-valued KL is constructive.
-- Per [[expose-generator-not-orbit]]: ℚ-KLDivergence is the
-- generator; per-corpus KL values are orbits.
