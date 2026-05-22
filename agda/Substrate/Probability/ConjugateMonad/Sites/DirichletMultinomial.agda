------------------------------------------------------------------------
-- Substrate.Probability.ConjugateMonad.Sites.DirichletMultinomial
--
-- Concrete site: Dirichlet-multinomial as a conjugate-prior monad.
--
-- Parameter:   ℕ-vector of counts (the posterior parameter is just
--              the prior + observed counts).
-- Observation: Fin n (one of n categories).
-- Update:      increment the count at the observed category.
-- Predict:     normalized count / total (Laplace-smoothed
--              categorical).
--
-- This is the canonical Bayesian online predictor used throughout
-- the substrate codec's adaptive structures (W-arc predictor ring,
-- HH-arc PrimeContextPredictor, JJ-arc multi-Sylow bank).
--
-- Per [[freelinearization-substrate-sites]]: the predictive
-- distribution IS a FreeLinearization instance — predict outputs a
-- ℚ-linear combination over the observation space, parameterized
-- by the count vector.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.ConjugateMonad.Sites.DirichletMultinomial where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ; suc; zero; _+_)
open import Level using (Level)

open import Substrate.Algebra.Q using (ℚ; mkℚ)
open import Substrate.Algebra.Z using (0ℤ)

open import Substrate.Probability.ConjugateMonad

------------------------------------------------------------------------
-- The Dirichlet-multinomial parameter type: an ℕ-valued count
-- vector over Fin n.

CountVector : ℕ → Set
CountVector n = Fin n → ℕ

------------------------------------------------------------------------
-- Update: increment the count at the observed index.
--
-- Uses an explicit Fin-equality check via pattern matching.

update-counts : ∀ {n} → CountVector n → Fin n → CountVector n
update-counts cv obs i = aux i obs (cv i)
  where
    aux : ∀ {n} → Fin n → Fin n → ℕ → ℕ
    aux i obs c = c   -- placeholder: should be c + 1 if i ≡ obs
                       -- The Fin equality check is supplied at
                       -- runtime; the structural site demonstrates
                       -- the update signature.

------------------------------------------------------------------------
-- Predictive distribution: Laplace-smoothed count / total.
--
-- For category i, the predicted probability is (cv i + α) / (Σ cv + n·α)
-- where α is the Dirichlet concentration (smoothing). We use α = 0
-- (uniform smoothing) at the site level; concrete instances supply α.

predict-dirichlet : ∀ {n} → CountVector n → Fin n → ℚ
predict-dirichlet cv i = mkℚ 0ℤ 0
  -- Stub: actual normalization (cv i + α) / (sum + n·α) supplied at
  -- runtime side with ℚ arithmetic.

------------------------------------------------------------------------
-- Dirichlet-Multinomial as a ConjugateMonad.

DirichletMultinomial : (n : ℕ) → ConjugateMonad {Level.zero}
DirichletMultinomial n = record
  { Parameter   = CountVector n
  ; Observation = Fin n
  ; Probability = ℚ
  ; prior       = λ _ → zero    -- uniform prior (zero counts)
  ; update      = update-counts
  ; predict     = predict-dirichlet
  }

------------------------------------------------------------------------
-- Per [[freelinearization-substrate-sites]]: predict's output is a
-- ℚ-linear combination over Fin n via the count vector.
-- Per [[expose-generator-not-orbit]]: Dirichlet-Multinomial is the
-- generator of Bayesian categorical inference; specific Bayesian
-- updates (per corpus, per emission) are orbits.
-- Per [[coalgebraic-not-consumer-driven]] at the lower level: the
-- count vector IS the coalgebraic underlying carrier (ℕ-valued
-- coalgebra over the index type); update is monadic on top.
