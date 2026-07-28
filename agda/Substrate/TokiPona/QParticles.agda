------------------------------------------------------------------------
-- Substrate.TokiPona.QParticles
--
-- TPQ5 of the Toki Pona ℚ-retrofit arc per [scratch/tpq_arc_plan.md].
--
-- Particle markers re-used from the F₂ original (T6). Particles
-- don't get richer in ℚ: they're discrete structural markers
-- (li / e / pi / la / o), not semantic vectors. The marker layer
-- is shared between the F₂ and ℚ Toki Pona arcs.
--
-- This slice provides a thin re-export + a paired-with-Q-sentence
-- record for downstream marker+semantic-vector use.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.QParticles where

open import Substrate.Foundation.Nat using (ℕ)

-- Re-export the F₂ Particles infrastructure (which is F₂-graded
-- but is about structural markers, not semantic vectors).
open import Substrate.TokiPona.Particles
  using (Particle; li; e; pi; la; o;
         MarkerSet; mkMarkers; no-markers;
         set-particle; merge-markers)
open import Substrate.TokiPona.QTokiSentence using (QTokiSentence)

------------------------------------------------------------------------
-- 1. Q-MarkedSentence: pairs a Q-sentence with a MarkerSet.
------------------------------------------------------------------------

record QMarkedSentence (m : ℕ) : Set where
  constructor mkQMarked
  field
    q-sentence : QTokiSentence m
    markers    : MarkerSet


open QMarkedSentence public
------------------------------------------------------------------------
-- 2. Constructors.
------------------------------------------------------------------------

mark-Q : {m : ℕ} → QTokiSentence m → QMarkedSentence m
mark-Q s = mkQMarked s no-markers

with-Q-particle : {m : ℕ} → Particle → QMarkedSentence m → QMarkedSentence m
with-Q-particle p ms = mkQMarked
  (q-sentence ms)
  (merge-markers (markers ms) (set-particle p))

------------------------------------------------------------------------
-- 3. Capstone for TPQ5.
--
-- ℚ-particle layer (re-uses F₂ marker infrastructure since
-- particles are structural, not semantic). TPQ6 packages the
-- coherence laws; TPQ7 the universal property.
------------------------------------------------------------------------
