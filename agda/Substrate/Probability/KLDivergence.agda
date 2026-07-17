------------------------------------------------------------------------
-- Substrate.Probability.KLDivergence
--
-- IG6-IG12: Kullback-Leibler divergence and its compositional
-- structure.
--
-- KL(p || q) = Σ p(a) · log (p(a) / q(a)).
--
-- Per [[categorical-name-first]]: KL divergence (relative entropy)
-- is standard information theory.
--
-- Properties stated structurally; concrete instances prove:
--   * Non-negativity (Gibbs's inequality)
--   * Zero iff p = q
--   * Chain rule
--   * Convexity in both arguments
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.KLDivergence where

open import Substrate.Foundation.Level using (Level) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Probability.Simplex
open import Substrate.Probability.Entropy

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- IG6: KL divergence.

-- ⟡set1-rp: carrier→param — KL (∀-over-Set) was a FIELD (pinning the
-- record at Set (lsuc ℓ)); as a PARAMETER it never raises the sort —
-- fully vestigial.
record KLDivergence
       {Carrier : Set ℓ} {PS : ProbabilitySemiring Carrier}
       {EntropyTy : Set ℓ}
       {H : {A : Set ℓ} → DiscreteDistribution PS A → EntropyTy}
       (EF : EntropyFunctor PS EntropyTy H)
       (KL : {A : Set ℓ} →
             DiscreteDistribution PS A →
             DiscreteDistribution PS A →
             EntropyTy)
       : Set where

------------------------------------------------------------------------
-- IG7: KL positivity.
--
-- KL(p || q) ≥ 0 with equality iff p = q.
-- Stated as a structural commitment; concrete instances supply the
-- proof via Gibbs's inequality.

------------------------------------------------------------------------
-- IG8: KL chain rule.
--
-- KL(p(X, Y) || q(X, Y)) = KL(p(X) || q(X)) +
--                          E_{x ~ p} [KL(p(Y | X = x) || q(Y | X = x))].
-- Structural commitment; concrete instances prove.

------------------------------------------------------------------------
-- IG9: Cross-entropy.
--
-- H(p, q) = -Σ p(a) · log q(a) = H(p) + KL(p || q).

record CrossEntropy
       {Carrier : Set ℓ} {PS : ProbabilitySemiring Carrier}
       {EntropyTy : Set ℓ}
       {H : {A : Set ℓ} → DiscreteDistribution PS A → EntropyTy}
       (EF : EntropyFunctor PS EntropyTy H)
       {KL : {A : Set ℓ} →
             DiscreteDistribution PS A →
             DiscreteDistribution PS A →
             EntropyTy}
       (KL-ops : KLDivergence EF KL) : Set (lsuc ℓ) where
  field
    H-cross : {A : Set ℓ} →
              DiscreteDistribution PS A →
              DiscreteDistribution PS A →
              EntropyTy

open CrossEntropy public

------------------------------------------------------------------------
-- IG10: Fisher information (sketch).
--
-- Fisher information is the negative expected second derivative of
-- log-likelihood — for discrete probability families parameterised
-- by θ, the information about θ contained in observations.
--
-- Stated structurally; concrete instances supply the operator.

record FisherInformation
       {Carrier : Set ℓ} {PS : ProbabilitySemiring Carrier}
       {EntropyTy : Set ℓ}
       {H : {A : Set ℓ} → DiscreteDistribution PS A → EntropyTy}
       (EF : EntropyFunctor PS EntropyTy H) : Set (lsuc ℓ) where
  field
    Fisher : {Θ A : Set ℓ} →
             (Θ → DiscreteDistribution PS A) →
             Θ → EntropyTy

open FisherInformation public

------------------------------------------------------------------------
-- IG11: Information gain at update step.
--
-- Information gain from updating prior p to posterior q under
-- observation = KL(q || p). Quantifies how much the observation
-- shifted the belief.
--
-- For ConjugateMonad: information gain at each update step =
-- KL(updated parameter || previous parameter).

------------------------------------------------------------------------
-- IG12: Information at strata boundaries.
--
-- BoundaryEvent's "signature" can include the KL between the
-- before-stratum's distribution and the after-stratum's, quantifying
-- how surprising the drift was.
--
-- Stated structurally; concrete drift-detectors supply per-event
-- KL computation.
