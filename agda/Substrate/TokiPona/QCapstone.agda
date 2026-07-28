------------------------------------------------------------------------
-- Substrate.TokiPona.QCapstone
--
-- TPQ10 of the Toki Pona ℚ-retrofit arc per [scratch/tpq_arc_plan.md].
--
-- Capstone: re-export of TPQ1-TPQ9 + summary of the arc's
-- contributions + connection to the original F₂ Toki Pona arc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.QCapstone where

-- Re-export the TPQ-arc slices publicly.
open import Substrate.TokiPona.QSemanticSpace
open import Substrate.TokiPona.QNimiSpace
open import Substrate.TokiPona.QModifierBilinear
open import Substrate.TokiPona.QTokiSentence
open import Substrate.TokiPona.QParticles
open import Substrate.TokiPona.QLinearity
open import Substrate.TokiPona.QLinearAlgebra
open import Substrate.TokiPona.F2toQForget
open import Substrate.TokiPona.QFragment
------------------------------------------------------------------------
-- 1. Cross-arc consistency note.
--
-- The original F₂ Toki Pona arc (Substrate.TokiPona.*) remains
-- intact as the substrate-internal demonstration fragment. The
-- ℚ version (this arc) is the carrier for any consumer needing
-- richer semantics. The F2toQForget functor (TPQ8) demonstrates
-- the original arc embeds into this one.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 2. Capstone for the TPQ-arc.
--
-- After this slice, the substrate has:
--   * ℚ-valued semantic carrier (TPQ1) for Toki Pona
--   * One-hot ℚ-NimiSpace + parametric richer-image hook (TPQ2)
--   * Two ℚ-modifier ops: sum (feature union) + product
--     (feature intersection, GENUINELY bilinear over ℚ) (TPQ3)
--   * ℚ-TokiSentence with sum/prod interpretations (TPQ4)
--   * Q-Particle marker layer (re-using F₂ infrastructure) (TPQ5)
--   * QLinearity coherence record + canonical instance (TPQ6)
--   * QNimiFreeLinearization + identity instance (TPQ7)
--   * F₂ → ℚ forgetful functor (TPQ8)
--   * Worked examples (TPQ9)
--
-- The 20-slice sprint FLQ-arc + TPQ-arc closes:
--   * FreeLinearization generalised from F₂ to parametric R (FLQ)
--   * Toki Pona's "ℝ-vectors deferred until ℚ exists" obligation
--     discharged via ℚ-retrofit (TPQ)
--
-- Future arcs:
--   * ℚ-linear-extensionality lemma to complete ℚ-FreeLinearization
--   * Toki Pona consumer using rich (non-one-hot) ℚ-image maps
--   * ℚ-modifier-bilinearity proofs (associativity, distributivity)
--   * Generalising FLQ to abstract ring R (beyond F₂ and ℚ)
------------------------------------------------------------------------
