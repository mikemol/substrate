------------------------------------------------------------------------
-- Substrate.TokiPona.QNimiSpace
--
-- TPQ2 of the Toki Pona ℚ-retrofit arc per [scratch/tpq_arc_plan.md].
--
-- Each nimi gets a ℚ-basis vector via the FLQ-arc's
-- ℚ-LinearAlgebra. Sister to T3 NimiSpace which used F₂-basis.
--
-- The one-hot embedding (each nimi → its basis ℚ-vector) is the
-- canonical instantiation. Richer semantics (per-nimi weighted
-- ℚ-vectors capturing real distributional content) are
-- per-consumer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.QNimiSpace where

open import Substrate.Foundation.Nat using (ℕ)

open import Substrate.TokiPona.Nimi using (Nimi; nimi-count; nimi-index)
open import Substrate.Algebra.Q.Vector using (basis-ℚ)
open import Substrate.TokiPona.QSemanticSpace using (QSemVec)

------------------------------------------------------------------------
-- 1. One-hot ℚ-embedding.
--
-- Each nimi maps to its corresponding ℚ-basis vector in
-- QSemVec nimi-count.
------------------------------------------------------------------------

nimi-as-Q-vector : Nimi → QSemVec nimi-count
nimi-as-Q-vector n = basis-ℚ (nimi-index n)

------------------------------------------------------------------------
-- 2. The richer-semantics signature.
--
-- A consumer providing a per-nimi ℚ-vector image map (rather than
-- one-hot) can lift it through ℚ-LinearAlgebra's universal
-- property. This sub-module exposes the API.
------------------------------------------------------------------------

module WithRichImage
  {m : ℕ}
  (image : Nimi → QSemVec m)
  where

  nimi-rich-image : Nimi → QSemVec m
  nimi-rich-image = image

------------------------------------------------------------------------
-- 3. Capstone for TPQ2.
--
-- ℚ-NimiSpace defined via one-hot embedding + parametric richer-
-- image module. TPQ3 builds the ℚ-bilinear modifier composition.
------------------------------------------------------------------------
