------------------------------------------------------------------------
-- Substrate.Linguistic.Classification.ClassCompwitnessByClass
--
-- Defines: class∘witness-by-class
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.Classification; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Classification.ClassCompwitnessByClass where

open import Substrate.Category.FreeOverBasis
open import Substrate.Linguistic.Roster.BasisOf
open import Substrate.Linguistic.Roster.FreeCarrierOf
open import Substrate.Linguistic.Roster.Lang
open import Substrate.Linguistic.Roster.WitnessOf
open import Substrate.Foundation.Eq
open import Substrate.Linguistic.Classification.WitnessByClass
open import Substrate.Linguistic.Classification.SumOR



class∘witness-by-class :
  (c : FreeConstructionClass) →
  (c ≡ Free-other) ⊎-OR (class (witness-of (witness-by-class c)) ≡ c)
class∘witness-by-class Free-monoid    = there refl
class∘witness-by-class Free-F2-module = there refl
class∘witness-by-class Free-cyclic    = there refl
class∘witness-by-class Free-relation  = there refl
class∘witness-by-class Free-CCC       = there refl
class∘witness-by-class Free-Lie       = there refl
class∘witness-by-class Free-other     = here refl
