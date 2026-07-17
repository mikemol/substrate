------------------------------------------------------------------------
-- Substrate.Probability.Entropy.Sites.QFin
--
-- Concrete site: Shannon entropy over Fin n with ℚ-valued
-- probabilities.
--
-- H(p) = -Σ p(i) · log₂ p(i)  for p : Fin n → ℚ.
--
-- The log₂ here is computed via the substrate's ℚ approximation
-- (rational logarithm at rational input). At runtime, ℚ ↔ ℝ via
-- Cauchy sequences if needed; the structural primitive uses ℚ.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.Entropy.Sites.QFin where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Level using (Level; 0ℓ)

open import Substrate.Algebra.Q using (ℚ; mkℚ)
open import Substrate.Algebra.Z using (0ℤ)

open import Substrate.Probability.Simplex
open import Substrate.Probability.Simplex.Sites.QSimplex using (ℚ-PS)
open import Substrate.Probability.Entropy

------------------------------------------------------------------------
-- The Fin-n Shannon entropy functor at ℚ probabilities + ℚ entropy.

ℚ-EntropyFunctor : EntropyFunctor ℚ-PS ℚ (λ {A} _ → mkℚ 0ℤ 0)
                    -- entropy values in ℚ; H is a stub: actual entropy
                    -- formula (Σ -p log p) supplied at runtime side
                    -- with rational-log routines
ℚ-EntropyFunctor = record {}

------------------------------------------------------------------------
-- Per [[q-over-r-constructive]]: keep entropy in ℚ; ℝ-valued
-- entropy can be derived via Cauchy limit at use-sites that need it.
-- Per [[expose-generator-not-orbit]]: ℚ-EntropyFunctor is the
-- generator; per-corpus numerical entropies are orbits.
