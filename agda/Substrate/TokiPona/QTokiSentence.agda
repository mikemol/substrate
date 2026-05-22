------------------------------------------------------------------------
-- Substrate.TokiPona.QTokiSentence
--
-- TPQ4 of the Toki Pona ℚ-retrofit arc per [scratch/tpq_arc_plan.md].
--
-- ℚ-valued Toki Pona sentence: subject + predicate + object as
-- ℚ-vectors with a parametric interpretation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.QTokiSentence where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.TokiPona.QSemanticSpace using (QSemVec; ∅-Q; _⊕Q_)
open import Substrate.TokiPona.QModifierBilinear
  using (modify-Q-sum; modify-Q-prod; _·ℚⱽ_)

------------------------------------------------------------------------
-- 1. The Q-TokiSentence record.
------------------------------------------------------------------------

record QTokiSentence (m : ℕ) : Set where
  constructor mkQSentence
  field
    subject   : QSemVec m
    predicate : QSemVec m
    object    : QSemVec m

open QTokiSentence public

------------------------------------------------------------------------
-- 2. Interpretation: feature-union via vector sum.
--
-- A consumer wanting the feature-intersection reading would use
-- interpret-prod instead.
------------------------------------------------------------------------

interpret-sum : {m : ℕ} → QTokiSentence m → QSemVec m
interpret-sum s =
  modify-Q-sum (modify-Q-sum (subject s) (predicate s)) (object s)

interpret-prod : {m : ℕ} → QTokiSentence m → QSemVec m
interpret-prod s =
  modify-Q-prod (modify-Q-prod (subject s) (predicate s)) (object s)

------------------------------------------------------------------------
-- 3. Constructors for sentence shapes.
------------------------------------------------------------------------

Q-intransitive : {m : ℕ} → QSemVec m → QSemVec m → QTokiSentence m
Q-intransitive subj pred = mkQSentence subj pred ∅-Q

Q-transitive : {m : ℕ} → QSemVec m → QSemVec m → QSemVec m → QTokiSentence m
Q-transitive subj pred obj = mkQSentence subj pred obj

------------------------------------------------------------------------
-- 4. Capstone for TPQ4.
--
-- ℚ-TokiSentence + two interpretation modes (sum / prod) defined.
-- TPQ5 builds the particle marker layer.
------------------------------------------------------------------------
