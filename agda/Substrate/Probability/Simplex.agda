------------------------------------------------------------------------
-- Substrate.Probability.Simplex
--
-- IG1: finite probability simplex. The set of probability
-- distributions over a finite alphabet of size n is the
-- (n-1)-dimensional simplex Δⁿ⁻¹.
--
-- Per [[q-over-r-constructive]]: probabilities live in ℚ ∩ [0, 1]
-- (rationals; constructive). This module abstracts the probability
-- type as a parameterised Probability with the structural
-- assumptions needed (zero, one, plus, sum-to-one).
--
-- A discrete probability distribution over a finite type A is a
-- function A → Probability (the sum-to-one law is a separate
-- structural commitment supplied by concrete instances, not enforced
-- by this record).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.Simplex where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Level using (Level; 0ℓ) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- Abstract probability semiring (zero, one, plus). Concrete
-- instances: ℚ ∩ [0, 1] for rational probabilities; ℝ ∩ [0, 1] for
-- real probabilities (not used in --safe due to non-constructivity).

record ProbabilitySemiring : Set (lsuc ℓ) where
  field
    Carrier : Set ℓ
    zero-p  : Carrier
    one-p   : Carrier
    plus-p  : Carrier → Carrier → Carrier

open ProbabilitySemiring public

------------------------------------------------------------------------
-- A discrete probability distribution over a finite type A.
--
-- Probabilities are a function A → Carrier; the sum-to-one law
-- (∑ p a = one) is a separate structural commitment.

record DiscreteDistribution
       (PS : ProbabilitySemiring {ℓ})
       (A : Set ℓ) : Set ℓ where
  field
    pmf      : A → Carrier PS
    -- sum-to-one is stated abstractly; concrete instances either
    -- compute the sum and prove it equals one-p, or supply the
    -- sum-folding operator explicitly.

open DiscreteDistribution public

------------------------------------------------------------------------
-- The simplex over Fin n.
--
-- Δⁿ⁻¹ = { p : Fin n → Carrier | sum p ≡ one } (set-builder is prose:
-- the `sum p ≡ one` predicate is NOT enforced by the type below —
-- concrete instances supply the sum operator and the proof).

-- Simplex over Fin n at level 0 — needs a non-polymorphic
-- ProbabilitySemiring at level 0. Concrete instances supply.

Simplex : ProbabilitySemiring {0ℓ} → ℕ → Set
Simplex PS n = DiscreteDistribution PS (Fin n)
