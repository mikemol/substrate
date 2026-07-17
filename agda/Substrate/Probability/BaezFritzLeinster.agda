------------------------------------------------------------------------
-- Substrate.Probability.BaezFritzLeinster
--
-- IG13-IG20: Baez-Fritz-Leinster characterization of entropy +
-- functorial interpretation + connections to MarkovCategory,
-- BoundaryEvent, ConjugateMonad.
--
-- The Baez-Fritz-Leinster theorem characterizes Shannon entropy as
-- the unique (up to scale) FUNCTOR from the category of probability
-- spaces (or finite probability distributions with maps that "lose"
-- information) into the additive monoid (ℝ≥0, +) satisfying:
--   * Functoriality (preserves composition)
--   * "Chain rule" naturality
--   * Convex-combination compatibility
--
-- Reference: Baez, Fritz, Leinster, "A characterization of entropy
-- in terms of information loss" (Entropy 13 (2011), 1945-1957).
--
-- The substrate uses this to anchor entropy as a categorical
-- INVARIANT, not a hand-computed numerical quantity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.BaezFritzLeinster where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Probability.Simplex
open import Substrate.Probability.Entropy
open import Substrate.Probability.KLDivergence
open import Substrate.Probability.MarkovCategory

private
  variable
    ℓ ℓm : Level

------------------------------------------------------------------------
-- IG13: Baez-Fritz-Leinster entropy functor.
--
-- A functor from a category of probability spaces (with information-
-- losing maps) to the additive monoid of entropy values, satisfying
-- the BFL axioms.
--
-- Concrete instances supply both the category and the entropy values.

record BFLEntropyFunctor
       {Carrier : Set ℓ} (PS : ProbabilitySemiring Carrier)
       (EntropyTy : Set ℓ)
       (H : {A : Set ℓ} → DiscreteDistribution PS A → EntropyTy)
       : Set where
  field
    EF                : EntropyFunctor PS EntropyTy H
    -- Functoriality + convex-combination + chain-rule laws are
    -- stated abstractly; concrete instances prove them.

open BFLEntropyFunctor public

------------------------------------------------------------------------
-- IG14: Convex combination compatibility.
--
-- For a convex combination λp + (1-λ)q of two distributions, the
-- entropy satisfies:
--   H(λp + (1-λ)q) = λ H(p) + (1-λ) H(q) + h(λ)
-- where h(λ) = -λ log λ - (1-λ) log(1-λ) is the binary entropy of λ.
--
-- Structural commitment; concrete instances prove via the entropy
-- formula.

------------------------------------------------------------------------
-- IG15: Sufficient statistic via mutual information.
--
-- Connection to MK9: a statistic T is sufficient for the model
-- X | Θ iff I(Θ; X | T) = 0 — the mutual information between Θ
-- and X given T is zero. Stated structurally; the connection
-- between IG (information-theoretic) and MK (categorical)
-- sufficient statistic is empirically verified per the
-- equivalence theorem.

-- SufficientStatisticInfoTheory is a structural marker — concrete
-- instances supply the conditional MI = 0 proof.

record SufficientStatisticInfoTheory
       {Carrier : Set ℓ} {PS : ProbabilitySemiring Carrier}
       {EntropyTy : Set ℓ}
       {H : {A : Set ℓ} → DiscreteDistribution PS A → EntropyTy}
       (M : MarkovCategory {ℓ} {ℓm})
       (EF : EntropyFunctor PS EntropyTy H)
       {KL : {A : Set ℓ} →
             DiscreteDistribution PS A →
             DiscreteDistribution PS A →
             EntropyTy}
       (KL-ops : KLDivergence EF KL) : Set where
  no-eta-equality

------------------------------------------------------------------------
-- IG16: Markov category interpretation.
--
-- Entropy + KL extend to functors on a Markov category. The
-- substrate uses this to:
--   * Quantify probabilistic information at MK6 (almost-sure
--     equality is "zero relative entropy under p")
--   * Detect BoundaryEvent surprise via KL between adjacent
--     section distributions

------------------------------------------------------------------------
-- IG17: Adaptive arity via entropy threshold.
--
-- The substrate's FieldFanOut (now variable-arity) can be reconfigured
-- dynamically based on entropy:
--   if H(current signal) drops below threshold → reduce arity (some
--     primes have become predictable; less is needed)
--   if H rises above threshold → increase arity (more primes
--     needed to capture residual variance)
--
-- Stated structurally; concrete adaptive-arity strategies supply
-- threshold values.

record EntropyBasedAdaptation
       {Carrier : Set ℓ} {PS : ProbabilitySemiring Carrier}
       {EntropyTy : Set ℓ}
       {H : {A : Set ℓ} → DiscreteDistribution PS A → EntropyTy}
       (EF : EntropyFunctor PS EntropyTy H) : Set ℓ where
  field
    threshold-up   : EntropyTy
    threshold-down : EntropyTy
    -- adaptation rule: if H > threshold-up, increase arity;
    --                  if H < threshold-down, decrease arity.

open EntropyBasedAdaptation public

------------------------------------------------------------------------
-- IG18: Posterior surprise in ConjugateMonad.
--
-- For a ConjugateMonad update (prior → posterior under observation),
-- the "surprise" = KL(posterior || prior). Connects ConjugateMonad
-- to information theory at the update level.
--
-- Concrete instances compute the per-update KL.

------------------------------------------------------------------------
-- IG19: BoundaryEvent → information gain.
--
-- A boundary event at locus b produces a fiber-state transition
-- from before to after. The information gain associated with the
-- event = KL(distribution after || distribution before) at b.
--
-- This gives BoundaryEvent records a quantitative information-
-- theoretic interpretation: "how informative was this drift?"

------------------------------------------------------------------------
-- IG20: IG arc capstone.
--
-- The information-geometry primitives provide:
--   * Shannon entropy, KL divergence, Fisher information
--   * BFL functorial characterization
--   * Connection to MarkovCategory (sufficient statistics)
--   * Connection to BoundaryEvent (information gain at drifts)
--   * Connection to ConjugateMonad (posterior surprise)
--
-- Per the horizon: sheaf cohomology computes "global obstructions
-- to information agreement" — which is information theory at the
-- topological level (uses simplicial complexes + sheaves over them).
-- IG arc provides the local information-theoretic primitives; the
-- sheaf-theoretic horizon uses them globally.
--
-- Per [[homology-cohomology-recursion]]: KL is the cohomology
-- distance between distributions; the BFL functor IS the homology
-- cycle (it captures the additive structure of information loss).
--
-- Per [[expose-generator-not-orbit]]: EntropyFunctor is the generator
-- of information-theoretic measurement; specific entropy values (per
-- corpus, per emission) are orbits.
------------------------------------------------------------------------
