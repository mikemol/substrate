------------------------------------------------------------------------
-- Substrate.Probability.Entropy
--
-- IG2-IG5: Shannon entropy, conditional entropy, joint entropy,
-- mutual information.
--
-- Per [[categorical-name-first]]: Shannon entropy, conditional
-- entropy, joint entropy, mutual information are standard
-- information theory.
--
-- Per the Baez-Fritz-Leinster characterization (IG13): Shannon
-- entropy is the UNIQUE (up to scale) function on probability
-- distributions satisfying:
--   * Continuity
--   * Symmetry under relabelling
--   * Additivity over Cartesian products
--   * Convex-combination compatibility
--
-- The substrate captures the structural definition + laws; concrete
-- numerical entropy values are computed at the runtime side.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.Entropy where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Level using (Level) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Probability.Simplex

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- IG2: Shannon entropy.
--
-- H(p) = -Σ p(a) · log p(a).
--
-- Parameterised by a probability semiring with a "negative log"
-- operator. Concrete instances supply log over their probability
-- type (e.g., log₂ over ℚ ∩ (0, 1]).

record EntropyFunctor : Set (lsuc ℓ) where
  field
    PS         : ProbabilitySemiring {ℓ}
    EntropyTy  : Set ℓ        -- target type for entropy values
                              -- (typically ℝ or ℚ-extended)
    H          : {A : Set ℓ} →
                 DiscreteDistribution PS A →
                 EntropyTy

open EntropyFunctor public

------------------------------------------------------------------------
-- IG3: Conditional entropy H(X | Y) = H(X, Y) - H(Y).
--
-- Parameterised over the joint and marginal distributions; concrete
-- instances supply both.

record ConditionalEntropy
       (EF : EntropyFunctor {ℓ}) : Set (lsuc ℓ) where
  field
    H-cond : {A B : Set ℓ} →
             DiscreteDistribution (PS EF) A →
             DiscreteDistribution (PS EF) B →
             EntropyTy EF

open ConditionalEntropy public

------------------------------------------------------------------------
-- IG4: Joint entropy H(X, Y) = H over the product distribution.

record JointEntropy
       (EF : EntropyFunctor {ℓ}) : Set (lsuc ℓ) where
  field
    H-joint : {A B : Set ℓ} →
              DiscreteDistribution (PS EF) A →
              DiscreteDistribution (PS EF) B →
              EntropyTy EF

open JointEntropy public

------------------------------------------------------------------------
-- IG5: Mutual information I(X; Y) = H(X) + H(Y) - H(X, Y).
--
-- Concrete instances supply the operation given an EntropyFunctor +
-- JointEntropy.

record MutualInformation
       (EF : EntropyFunctor {ℓ})
       (JE : JointEntropy EF) : Set (lsuc ℓ) where
  field
    MI : {A B : Set ℓ} →
         DiscreteDistribution (PS EF) A →
         DiscreteDistribution (PS EF) B →
         EntropyTy EF

open MutualInformation public
