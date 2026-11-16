------------------------------------------------------------------------
-- Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment.TokiponaWitnessClass
--
-- Defines: tokipona-witness-class
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment.TokiponaWitnessClass where

open import Substrate.TokiPona.AsFreeOverBasis.TokiponaWitness
open import Substrate.Category.FreeOverBasis
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 3. Witness identity.
------------------------------------------------------------------------

tokipona-witness-class : class tokipona-witness ≡ Free-F2-module
tokipona-witness-class = refl
