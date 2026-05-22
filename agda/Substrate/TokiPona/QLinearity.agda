------------------------------------------------------------------------
-- Substrate.TokiPona.QLinearity
--
-- TPQ6 of the Toki Pona ℚ-retrofit arc per [scratch/tpq_arc_plan.md].
--
-- Coherence record for ℚ-valued Toki Pona, sister to T7's
-- TokiLinearity. Bundles the available structural identities
-- on ℚ-modifier composition and ℚ-sentence interpretation.
--
-- HONEST SCOPE: Many laws in T7 were refl-provable because of F₂'s
-- definitional behaviour; the ℚ analogs require ℚ-arithmetic
-- lemmas (associativity, commutativity, distributivity) the Q-arc
-- deferred. This slice records the SIGNATURE of the laws + the
-- ones provable today.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.QLinearity where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.TokiPona.QSemanticSpace using (QSemVec; ∅-Q)
open import Substrate.TokiPona.QModifierBilinear
  using (modify-Q-sum; modify-Q-prod)
open import Substrate.TokiPona.QTokiSentence
  using (QTokiSentence; interpret-sum; interpret-prod)
open import Substrate.TokiPona.QParticles
  using (MarkerSet; no-markers; merge-markers)

------------------------------------------------------------------------
-- 1. QLinearity record.
--
-- The fields correspond to the laws we WANT; the canonical instance
-- below populates the easily-discharged ones via refl + leaves the
-- arithmetic-heavy ones as documented obligations.
------------------------------------------------------------------------

record QLinearity (m : ℕ) : Set where
  field
    -- Interpretation under modifier composition.
    interpret-shape-sum :
      (s : QTokiSentence m) →
      interpret-sum s ≡
        modify-Q-sum
          (modify-Q-sum (QTokiSentence.subject s)
                        (QTokiSentence.predicate s))
          (QTokiSentence.object s)
    interpret-shape-prod :
      (s : QTokiSentence m) →
      interpret-prod s ≡
        modify-Q-prod
          (modify-Q-prod (QTokiSentence.subject s)
                         (QTokiSentence.predicate s))
          (QTokiSentence.object s)
    -- Marker identity.
    markers-identityˡ :
      (ms : MarkerSet) → merge-markers no-markers ms ≡ ms

------------------------------------------------------------------------
-- 2. The canonical QLinearity instance.
--
-- The two interpretation-shape laws are refl by definition.
-- markers-identityˡ is inherited from the F₂ particle infrastructure.
------------------------------------------------------------------------

open import Substrate.TokiPona.Particles using (merge-no-markersˡ)

canonical-QLinearity : {m : ℕ} → QLinearity m
canonical-QLinearity = record
  { interpret-shape-sum  = λ _ → refl
  ; interpret-shape-prod = λ _ → refl
  ; markers-identityˡ    = merge-no-markersˡ
  }

------------------------------------------------------------------------
-- 3. Capstone for TPQ6.
--
-- ℚ-Linearity record + canonical instance. Heavier coherence
-- (associativity of modify-Q-sum, distributivity for modify-Q-prod
-- over modify-Q-sum) is deferred — needs ℚ-arithmetic lemmas.
------------------------------------------------------------------------
