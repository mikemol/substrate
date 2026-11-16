------------------------------------------------------------------------
-- Substrate.Linguistic.RetroactiveAlignment.LambdaAligned
--
-- Defines: lambda-aligned
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RetroactiveAlignment.LambdaAligned where

open import Substrate.Category.FreeOverBasis
open import Substrate.Lambda.Fragment.LambdaWitness
open import Substrate.Foundation.Eq
open import Substrate.Linguistic.RetroactiveAlignment.WitnessAlignment



lambda-aligned : WitnessAlignment lambda-witness
lambda-aligned = record
  { expected-name  = Lambda
  ; expected-class = Free-CCC
  ; name-witness   = refl
  ; class-witness  = refl
  }
