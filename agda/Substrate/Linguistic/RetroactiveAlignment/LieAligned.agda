------------------------------------------------------------------------
-- Substrate.Linguistic.RetroactiveAlignment.LieAligned
--
-- Defines: lie-aligned
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RetroactiveAlignment.LieAligned where

open import Substrate.Category.FreeOverBasis
open import Substrate.Invented.LieFragment
open import Substrate.Foundation.Eq
open import Substrate.Linguistic.RetroactiveAlignment.WitnessAlignment



lie-aligned : WitnessAlignment lie-witness
lie-aligned = record
  { expected-name  = LieFrag
  ; expected-class = Free-Lie
  ; name-witness   = refl
  ; class-witness  = refl
  }
