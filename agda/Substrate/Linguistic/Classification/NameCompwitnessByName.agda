------------------------------------------------------------------------
-- Substrate.Linguistic.Classification.NameCompwitnessByName
--
-- Defines: name∘witness-by-name
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.Classification; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Classification.NameCompwitnessByName where

open import Substrate.Category.FreeOverBasis
open import Substrate.Linguistic.Roster.BasisOf
open import Substrate.Linguistic.Roster.FreeCarrierOf
open import Substrate.Linguistic.Roster.Lang
open import Substrate.Linguistic.Roster.WitnessOf
open import Substrate.Foundation.Eq
open import Substrate.Linguistic.Classification.WitnessByName



------------------------------------------------------------------------
-- 4. Round-trip coherence: name → witness → name preserves.
--
-- Each witness records its own name; lookup followed by name
-- recovery is the identity. Six refl cases.
------------------------------------------------------------------------

name∘witness-by-name : (n : WitnessName) → name (witness-of (witness-by-name n)) ≡ n
name∘witness-by-name Lojban   = refl
name∘witness-by-name TokiPona = refl
name∘witness-by-name Solresol = refl
name∘witness-by-name Kelen    = refl
name∘witness-by-name Lambda   = refl
name∘witness-by-name LieFrag  = refl
