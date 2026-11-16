------------------------------------------------------------------------
-- Substrate.Linguistic.Classification.WitnessByName
--
-- Defines: witness-by-name
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.Classification; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Classification.WitnessByName where

open import Substrate.Category.FreeOverBasis
open import Substrate.Linguistic.Roster.BasisOf
open import Substrate.Linguistic.Roster.FreeCarrierOf
open import Substrate.Linguistic.Roster.Lang
open import Substrate.Linguistic.Roster.WitnessOf



------------------------------------------------------------------------
-- 2. Lookup by WitnessName.
--
-- A six-case dispatch from the enum to the corresponding Lang value.
-- C9 uses this to display witness pairs in tables.
------------------------------------------------------------------------

witness-by-name : WitnessName → Lang
witness-by-name Lojban   = lojban
witness-by-name TokiPona = tokipona
witness-by-name Solresol = solresol
witness-by-name Kelen    = kelen
witness-by-name Lambda   = lambda-lang
witness-by-name LieFrag  = lie-lang
