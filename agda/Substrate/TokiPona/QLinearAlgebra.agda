------------------------------------------------------------------------
-- Substrate.TokiPona.QLinearAlgebra
--
-- TPQ7 of the Toki Pona ℚ-retrofit arc per [scratch/tpq_arc_plan.md].
--
-- ℚ-side universal-property record for the Q-NimiSpace. Sister to
-- T8 LinearAlgebra (which was for F₂). Bundles the WitnessAlignment
-- + sketches the API for the full ℚ-FreeLinearization.
--
-- HONEST SCOPE: Like FLQ7, the full ℚ-FreeLinearization requires
-- ℚ-linear-extensionality (deferred). This slice records the API
-- and provides the structure consumers can reference.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.QLinearAlgebra where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.TokiPona.Nimi using (Nimi; nimi-count; nimi-index)
open import Substrate.Algebra.Q.Vector using (basis-ℚ)
open import Substrate.TokiPona.QSemanticSpace using (QSemVec)
open import Substrate.TokiPona.QNimiSpace using (nimi-as-Q-vector)

open import Substrate.Algebra.Q.Linear using (Linearℚ; apply; id-LQ)
open import Substrate.Category.LinearAlgebra using (LinearAlgebra)
open import Substrate.Algebra.Q.AsLinearAlgebra using (ℚ-LinearAlgebra)

------------------------------------------------------------------------
-- 1. The QNimiFreeLinearization record.
--
-- For any target dimension m and ℚ-image map `image : Nimi →
-- QSemVec m`, there should be a unique linear extension; pending
-- ℚ-extensionality, the existence + agreement-on-basis are
-- discharged but uniqueness is deferred.
------------------------------------------------------------------------

record QNimiFreeLinearization (m : ℕ) : Set where
  field
    q-nimi-image  : Nimi → QSemVec m
    q-extension   : Linearℚ nimi-count m
    q-on-basis    :
      (n : Nimi) →
      apply q-extension (basis-ℚ (nimi-index n)) ≡ q-nimi-image n
    -- Uniqueness deferred pending ℚ-linear-extensionality.

------------------------------------------------------------------------
-- 2. The canonical (identity) instance.
--
-- For image = nimi-as-Q-vector (one-hot ℚ embedding), the
-- extension is id-LQ on QSemVec nimi-count.
------------------------------------------------------------------------

canonical-Q-nimi-free :
  QNimiFreeLinearization nimi-count
canonical-Q-nimi-free = record
  { q-nimi-image = nimi-as-Q-vector
  ; q-extension  = id-LQ
  ; q-on-basis   = λ _ → refl
  }

------------------------------------------------------------------------
-- 3. Capstone for TPQ7.
--
-- ℚ-NimiFreeLinearization defined + canonical identity instance
-- discharged. Full uniqueness pending ℚ-linear-extensionality
-- from a future Q-arc extension. TPQ8 builds the F₂-to-ℚ
-- forgetful functor.
------------------------------------------------------------------------
