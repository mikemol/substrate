------------------------------------------------------------------------
-- Substrate.TokiPona.QFragment
--
-- TPQ9 of the Toki Pona ℚ-retrofit arc per [scratch/tpq_arc_plan.md].
--
-- Worked examples demonstrating ℚ-weighted polysemy beyond what
-- F₂ could express. Each nimi can have a richer ℚ-vector image
-- with fractional activation weights, capturing the
-- distributional-semantics intuition more faithfully.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.QFragment where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.Z using (ℤ; +_; -suc_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; 0ℚ; 1ℚ)
open import Substrate.TokiPona.Nimi
  using (Nimi; jan; soweli; lili; pona; wawa; nimi-count)
open import Substrate.TokiPona.QSemanticSpace using (QSemVec; basis-ℚ)
open import Substrate.TokiPona.QNimiSpace using (nimi-as-Q-vector)
open import Substrate.TokiPona.QModifierBilinear
  using (modify-Q-sum; modify-Q-prod; _·ℚⱽ_)
open import Substrate.TokiPona.QTokiSentence
  using (QTokiSentence; Q-intransitive; interpret-sum)

------------------------------------------------------------------------
-- 1. Named rationals for demos.
------------------------------------------------------------------------

half : ℚ
half = mkℚ (+ 1) 1   -- 1/2

quarter : ℚ
quarter = mkℚ (+ 1) 3   -- 1/4

three-quarters : ℚ
three-quarters = mkℚ (+ 3) 3   -- 3/4

------------------------------------------------------------------------
-- 2. One-hot ℚ-NimiSpace example.
--
-- The simplest ℚ-vector for a nimi: its one-hot basis-ℚ vector.
-- This matches the F₂ encoding lifted by F2toQForget.
------------------------------------------------------------------------

example-soweli-one-hot : QSemVec nimi-count
example-soweli-one-hot = nimi-as-Q-vector soweli

------------------------------------------------------------------------
-- 3. ℚ-weighted "soweli lili" (small animal) via sum modifier.
--
-- Demonstrates feature-union: vector with both directions
-- activated. This is the F₂-style reading.
------------------------------------------------------------------------

example-soweli-lili-sum : QSemVec nimi-count
example-soweli-lili-sum =
  modify-Q-sum (nimi-as-Q-vector soweli) (nimi-as-Q-vector lili)

------------------------------------------------------------------------
-- 4. ℚ-weighted "soweli lili" via product modifier.
--
-- Demonstrates feature-intersection: for one-hot inputs at
-- different basis positions, this is zero. The product captures
-- the meaningful intersection of two RICH vectors (when both
-- have weights at the same positions).
------------------------------------------------------------------------

example-soweli-lili-prod : QSemVec nimi-count
example-soweli-lili-prod =
  modify-Q-prod (nimi-as-Q-vector soweli) (nimi-as-Q-vector lili)

------------------------------------------------------------------------
-- 5. Worked sentence: "soweli li pona" (the animal is good).
--
-- Subject = soweli, Predicate = pona. Interpreted under sum.
------------------------------------------------------------------------

example-soweli-li-pona-Q : QTokiSentence nimi-count
example-soweli-li-pona-Q =
  Q-intransitive
    (nimi-as-Q-vector soweli)
    (nimi-as-Q-vector pona)

------------------------------------------------------------------------
-- 6. Capstone for TPQ9.
--
-- ℚ-weighted polysemy examples demonstrate the richer carrier.
-- Real distributional Toki Pona semantics would use per-nimi
-- ℚ-vectors that aren't one-hot — captured by the
-- QNimiSpace.WithRichImage interface from TPQ2.
------------------------------------------------------------------------
