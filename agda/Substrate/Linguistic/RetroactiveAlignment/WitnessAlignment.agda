------------------------------------------------------------------------
-- Substrate.Linguistic.RetroactiveAlignment.WitnessAlignment
--
-- Defines: WitnessAlignment, class-witness, expected-class, expected-name, name-witness
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RetroactiveAlignment.WitnessAlignment where

open import Substrate.Category.FreeOverBasis
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 1. The alignment record.
--
-- For each witness: WitnessName + FreeConstructionClass + a small
-- alignment witness. The alignment is the equality
-- `class (witness-with-name n) ≡ expected-class n` plus
-- `name (witness-with-name n) ≡ n`.
------------------------------------------------------------------------

-- ⟡set1-paydown: no Set-valued fields (WitnessName, FreeConstructionClass
-- and the two ≡-witnesses are all Set-level; W is a PARAMETER, which does
-- not raise the record's sort) — the : Set₁ was over-annotation.
record WitnessAlignment {B F : Set} (W : LanguageWitness B F) : Set where
  field
    expected-name  : WitnessName
    expected-class : FreeConstructionClass
    name-witness   : name W ≡ expected-name
    class-witness  : class W ≡ expected-class


open WitnessAlignment public
