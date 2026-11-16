------------------------------------------------------------------------
-- Substrate.Linguistic.RetroactiveAlignment.SolresolAligned
--
-- Defines: solresol-aligned
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RetroactiveAlignment.SolresolAligned where

open import Substrate.Category.FreeOverBasis
open import Substrate.Solresol.Fragment.Witness
open import Substrate.Foundation.Eq
open import Substrate.Linguistic.RetroactiveAlignment.WitnessAlignment



solresol-aligned : WitnessAlignment solresol-witness
solresol-aligned = record
  { expected-name  = Solresol
  ; expected-class = Free-cyclic
  ; name-witness   = refl
  ; class-witness  = refl
  }
