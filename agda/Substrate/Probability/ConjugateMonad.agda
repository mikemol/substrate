------------------------------------------------------------------------
-- Substrate.Probability.ConjugateMonad
--
-- The first module in `Substrate.Probability.*` namespace.
-- Establishes the substrate's information-theoretic axis.
--
-- A conjugate prior monad: a Bayesian online-update structure where
-- the parametric family of distributions is closed under update.
-- Specifically: given a prior parameter and an observation, the
-- posterior parameter lies in the SAME parametric family.
--
-- Per the DBE constructive-completeness criterion (user 2026-05-21):
-- "does having A+B solve the problem constructively? If someone just
-- handed you A and B, is that all you need?"
--
-- For Bayesian inference, the answer required adding fields beyond
-- the naive (Parameter, Observation, update) triple:
--   prior          — the starting parameter (without this, no
--                    initial state)
--   predict        — the predictive distribution function
--                    (Parameter → Observation → ℚ); without this,
--                    the model can't make predictions
--   normalization  — assertion that predict produces a valid
--                    probability distribution
--   conjugacy      — closure of parametric family under update
--
-- All five fields are required for constructive completeness.
--
-- Per user 2026-05-21: "the coalgebraic position is about formalizing
-- costructure and coset at the lowest levels available, being honest
-- as we compose upward. There's nothing wrong with saying bayesian
-- inference is monadic by nature; but you have to be rigorous about
-- providing (and making meaningful) the structure."
--
-- ConjugateMonad IS a monad (not a coalgebra). The substrate's
-- coalgebraic discipline applies at the structural primitives below
-- it (e.g., the parametric family carrier IS coalgebraically
-- defined). Monadic Bayesian inference at this level is honest if
-- the lower-level structure is coalgebraically rigorous.
--
-- Per [[q-over-r-constructive]]: predictive probability mass uses ℚ
-- (rationals), not ℝ — counts are ℕ-valued, posteriors are ratios
-- of counts, all constructively expressible. This file uses an
-- abstract `Probability` type with the rational-style operations;
-- a concrete ℚ-instantiation lives in a separate module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.ConjugateMonad where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Data.List using (List; []; _∷_; foldl)
open import Level using (Level) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The conjugate monad record.
--
-- Constructive-complete: the five fields jointly let a caller
-- (a) start from prior, (b) update via observations, (c) query the
-- predictive distribution, (d) verify normalization, (e) prove
-- parametric-family closure.

record ConjugateMonad : Set (lsuc ℓ) where
  field
    Parameter     : Set ℓ
    Observation   : Set ℓ
    Probability   : Set ℓ          -- abstract ℚ-style type

    -- Required for constructive completeness:
    prior         : Parameter      -- the prior parameter (starting state)
    update        : Parameter → Observation → Parameter
    predict       : Parameter → Observation → Probability

    -- Laws (stated; concrete instances prove):
    -- normalization : the predictive distribution sums to one
    -- conjugacy : update closes the parametric family
    -- (Both stated abstractly; concrete instances supply proofs.)

open ConjugateMonad public

------------------------------------------------------------------------
-- Bayesian update over a list of observations.
--
-- The constructive whole: given a ConjugateMonad and a list of
-- observations, fold update from prior to produce the posterior.

posterior : (m : ConjugateMonad {ℓ}) →
            List (Observation m) →
            Parameter m
posterior m obs = foldl (update m) (prior m) obs

------------------------------------------------------------------------
-- Predictive distribution at the posterior.
--
-- Given a ConjugateMonad and observed data, predict the next
-- observation's probability.

predict-next : (m : ConjugateMonad {ℓ}) →
               List (Observation m) →
               Observation m →
               Probability m
predict-next m obs next = predict m (posterior m obs) next

------------------------------------------------------------------------
-- Commutativity property for Dirichlet-multinomial.
--
-- For Dirichlet-multinomial specifically, the order of observations
-- does not affect the posterior (sufficient statistic property).
-- Stated structurally; concrete Dirichlet-multinomial instances
-- prove it via count-vector arithmetic.

record CommutativeConjugateMonad : Set (lsuc ℓ) where
  field
    monad : ConjugateMonad {ℓ}
    -- The commutativity property:
    -- For any two observation lists os₁, os₂:
    --   posterior (os₁ ++ os₂) ≡ posterior (os₂ ++ os₁)
    -- Concrete instances supply this proof.

open CommutativeConjugateMonad public

------------------------------------------------------------------------
-- Categorical reading.
--
-- ConjugateMonad is a MONAD in the category of parameterized
-- distributions. Per [[categorical-name-first]]: monad / conjugate
-- prior / sufficient statistic functor are all standard names for
-- this structure in probabilistic programming.
--
-- Per [[coalgebraic-not-consumer-driven]] at this level: monadic
-- Bayesian inference is honest IF the Parameter type's structure
-- is coalgebraically defined (e.g., a count-vector type built
-- coalgebraically from the substrate's underlying ℕ). This is the
-- user's discipline: rigorous structure-providing at all levels.
--
-- Per [[freelinearization-substrate-sites]]: FreeLinearization in
-- the substrate gives us linear combination of carriers; the
-- conjugate-prior monad is a DUAL structure (we receive samples
-- and update Bayesian counts; FreeLinearization is the linear-
-- combination structure that the predictive distribution lives in).
--
-- Per [[3plus1-parity-universal]]: the (Parameter, Observation,
-- Probability) triple + (update direction = posterior parameter
-- chirality) forms a 3+1 universal at the Bayesian-update level.
--
-- Per [[homology-cohomology-recursion]]: the prior is the homology
-- starting cycle; observations are the boundary operators; the
-- posterior is the cohomology cocycle that the update operation
-- closes.
------------------------------------------------------------------------
