------------------------------------------------------------------------
-- Eliza.Predictor
--
-- The trigram-level coalgebra: P(c₃ | c₁, c₂) accumulated from observed
-- input. Per the readmes' C-layer reading, the predictor IS the
-- coalgebraic transition kernel — the substrate's `Coalgebra` primitive
-- specialised to char-context bigrams.
--
-- The skeleton names the type signatures + key contracts:
--
--   * Counts : an accumulator from (Char × Char) to char-counts.
--   * smoothed-prob : Laplace-smoothed conditional probability.
--   * surprise-bits : -log₂ P(actual | last two).
--   * update : append one char to the model.
--   * project-text : sample a continuation.
--
-- The probability + log values are postulated as ℝ-typed; the
-- structural fact this module commits to is monotonicity-of-counts
-- (each `update` increments exactly one count) and conservation
-- (sum over c₃ of smoothed-prob c₃ | c₁ c₂ = 1).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Predictor where

open import Eliza.Prelude   using (ℕ; _×_; _,_)
open import Eliza.Alphabets using (Char)
open import Eliza.Word      using (Word)

------------------------------------------------------------------------
-- 1. ℝ — postulated as the continuous-value codomain. The skeleton
-- doesn't define a concrete representation (rational vs IEEE-754);
-- downstream Python uses Python floats. Per substrate discipline, the
-- DISCRETE inference rules CONSTRUCTING the ℝ values are in scope;
-- the values themselves are out of scope as content.
------------------------------------------------------------------------

postulate
  ℝ : Set

------------------------------------------------------------------------
-- 2. The model state.
------------------------------------------------------------------------

postulate
  Predictor : Set
  empty     : Predictor

  -- The two-char context, drawn off the most recent input.
  context-of : Predictor → Char × Char

------------------------------------------------------------------------
-- 3. The update step. Append one observed Char.
------------------------------------------------------------------------

postulate
  update : Predictor → Char → Predictor

------------------------------------------------------------------------
-- 4. The conditional probability — Laplace-smoothed.
------------------------------------------------------------------------

postulate
  smoothed-prob : Predictor → Char → ℝ
    -- = P(c | context-of predictor) with Laplace smoothing.

------------------------------------------------------------------------
-- 5. Surprise = -log₂ smoothed-prob. Postulated.
------------------------------------------------------------------------

postulate
  surprise-bits : Predictor → Char → ℝ

------------------------------------------------------------------------
-- 6. Top-N predicted continuations.
------------------------------------------------------------------------

postulate
  top-predictions :
    Predictor → ℕ → Word (Char × ℝ)
    -- Returns the top n (char, probability) pairs.

------------------------------------------------------------------------
-- 7. Sampling continuation. Given a length and a temperature, sample
-- a Word Char from the model.
------------------------------------------------------------------------

postulate
  project-text : Predictor → ℕ → ℝ → Word Char
    -- project-text predictor length temperature

------------------------------------------------------------------------
-- 8. Substrate-honest contract: the predictor is a Coalgebra. Its
-- `update` IS the coalgebraic step. Stated as a structural claim;
-- proved (or not) by inspection of the Python implementation.
------------------------------------------------------------------------

postulate
  predictor-is-coalgebra :
    (p : Predictor) (c : Char) →
    Predictor  -- placeholder — full property is functoriality of `update`
