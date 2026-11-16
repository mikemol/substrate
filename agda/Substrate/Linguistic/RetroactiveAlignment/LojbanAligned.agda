------------------------------------------------------------------------
-- Substrate.Linguistic.RetroactiveAlignment.LojbanAligned
--
-- Defines: lojban-aligned
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RetroactiveAlignment.LojbanAligned where

open import Substrate.Category.FreeOverBasis
open import Substrate.Lojban.AsFreeOverBasis.LojbanWitness
open import Substrate.Foundation.Eq
open import Substrate.Linguistic.RetroactiveAlignment.WitnessAlignment


------------------------------------------------------------------------
-- 2. The six aligned witnesses.
------------------------------------------------------------------------

lojban-aligned : WitnessAlignment lojban-witness
lojban-aligned = record
  { expected-name  = Lojban
  ; expected-class = Free-monoid
  ; name-witness   = refl
  ; class-witness  = refl
  }
