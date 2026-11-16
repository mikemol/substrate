------------------------------------------------------------------------
-- Substrate.Kelen.Fragment.KelenWitness
--
-- Defines: kelen-witness
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.Fragment.KelenWitness where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Category.FreeOverBasis
open import Substrate.Kelen.Fragment.Relational
open import Substrate.Kelen.Fragment.KelenWord
open import Substrate.Kelen.Fragment.KelenFreeStructure



kelen-witness : LanguageWitness Relational KelenWord
kelen-witness = mkWitness
  Kelen
  kelen-free-structure
  Free-relation
