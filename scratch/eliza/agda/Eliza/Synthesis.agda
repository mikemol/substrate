------------------------------------------------------------------------
-- Eliza.Synthesis
--
-- Continuation generation. Two forms:
--
--   * Unbiased projection: sample directly from the trigram model.
--     `Eliza.Predictor.project-text`.
--
--   * Branched (axis-flipped) projection: at each sampling step,
--     compute the spectral delta of the trigram's preferred generator,
--     apply a sign-flip across (Fiedler, turbulence) axes, find the
--     generator whose delta best matches the flipped target, sample a
--     char in the trigram context emitting that generator. Three
--     branches per turn for the three non-identity sign-flip pairs.
--
-- Once `Eliza.Sequitur` is in, a third form becomes available:
--
--   * Grammar projection: expand nonterminals from the learned grammar
--     to produce long-range structurally consistent continuations.
--
-- The module names the type signatures; the algorithmic content lives
-- in the Python.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Synthesis where

open import Eliza.Prelude   using (ℕ; _×_)
open import Eliza.Alphabets using (Char; Chamber)
open import Eliza.Word      using (Word)
open import Eliza.Predictor using (Predictor; ℝ; project-text)
open import Eliza.Sequitur  using (Grammar)

------------------------------------------------------------------------
-- 1. The unbiased synthesis is delegated to the Predictor module.
------------------------------------------------------------------------

synth-actual : Predictor → ℕ → ℝ → Word Char
synth-actual = project-text

------------------------------------------------------------------------
-- 2. The branch labels. Three non-identity sign-flip pairs over
-- (Fiedler-axis, turbulence-axis).
------------------------------------------------------------------------

data BranchLabel : Set where
  Φ̄  : BranchLabel   -- Fiedler-flipped
  T̄  : BranchLabel   -- turbulence-flipped
  Φ̄T̄ : BranchLabel   -- both flipped

------------------------------------------------------------------------
-- 3. Branched synthesis. Takes the current chamber (the spectral
-- starting point for the sign-flip computation) and the trigram model.
------------------------------------------------------------------------

postulate
  synth-branch :
    Predictor → Chamber → BranchLabel → ℕ → ℝ →
    Word Char
    -- predictor, start-chamber, branch, length, temperature

------------------------------------------------------------------------
-- 4. Grammar-projected synthesis. Once a Sequitur grammar has rules,
-- a continuation can be assembled by random expansion of an existing
-- nonterminal — preserving long-range structure the trigram cannot.
------------------------------------------------------------------------

postulate
  synth-from-grammar :
    {α : Set} → Grammar α → ℕ → Word α
    -- grammar, length

------------------------------------------------------------------------
-- 5. The structural contract: branched syntheses walk DIFFERENT
-- chamber paths from the unbiased synthesis. Stated as a postulate
-- claim: the resulting Word Chamber from walking is different (under
-- the right premises).
------------------------------------------------------------------------

postulate
  branched-diverges :
    Set  -- placeholder; full statement requires Eliza.Trajectory
