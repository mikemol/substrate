------------------------------------------------------------------------
-- Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment.TokiponaWitnessName
--
-- Defines: tokipona-witness-name
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment.TokiponaWitnessName where

open import Substrate.TokiPona.AsFreeOverBasis.TokiponaWitness
open import Substrate.Category.FreeOverBasis
open import Substrate.Foundation.Eq



tokipona-witness-name : name tokipona-witness ≡ TokiPona
tokipona-witness-name = refl

------------------------------------------------------------------------
-- 4. Capstone.
--
-- The "shared parent extraction is deferred" note from T10
-- AsLinearBridge is SUPERSEDED on the Toki Pona side. Together
-- with D6 (the Lojban side), the parent primitive's coverage of
-- both arcs is now substrate-witnessed at the alignment-lemma
-- level.
--
-- D8 unifies D6 + D7 into a single substrate-internal
-- RetroactiveAlignment record.
------------------------------------------------------------------------
