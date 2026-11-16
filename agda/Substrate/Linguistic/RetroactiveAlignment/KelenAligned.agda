------------------------------------------------------------------------
-- Substrate.Linguistic.RetroactiveAlignment.KelenAligned
--
-- Defines: kelen-aligned
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RetroactiveAlignment.KelenAligned where

open import Substrate.Category.FreeOverBasis
open import Substrate.Kelen.Fragment.KelenWitness
open import Substrate.Foundation.Eq
open import Substrate.Linguistic.RetroactiveAlignment.WitnessAlignment



kelen-aligned : WitnessAlignment kelen-witness
kelen-aligned = record
  { expected-name  = Kelen
  ; expected-class = Free-relation
  ; name-witness   = refl
  ; class-witness  = refl
  }
