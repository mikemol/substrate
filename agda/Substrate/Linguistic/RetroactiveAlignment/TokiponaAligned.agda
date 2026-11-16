------------------------------------------------------------------------
-- Substrate.Linguistic.RetroactiveAlignment.TokiponaAligned
--
-- Defines: tokipona-aligned
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RetroactiveAlignment.TokiponaAligned where

open import Substrate.Category.FreeOverBasis
open import Substrate.TokiPona.AsFreeOverBasis.TokiponaWitness
open import Substrate.Foundation.Eq
open import Substrate.Linguistic.RetroactiveAlignment.WitnessAlignment



tokipona-aligned : WitnessAlignment tokipona-witness
tokipona-aligned = record
  { expected-name  = TokiPona
  ; expected-class = Free-F2-module
  ; name-witness   = refl
  ; class-witness  = refl
  }
