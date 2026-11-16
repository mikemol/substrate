------------------------------------------------------------------------
-- Substrate.Linguistic.Classification.WitnessByClass
--
-- Defines: witness-by-class
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.Classification; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Classification.WitnessByClass where

open import Substrate.Category.FreeOverBasis
open import Substrate.Linguistic.Roster.BasisOf
open import Substrate.Linguistic.Roster.FreeCarrierOf
open import Substrate.Linguistic.Roster.Lang
open import Substrate.Linguistic.Roster.WitnessOf



------------------------------------------------------------------------
-- 3. Lookup by FreeConstructionClass.
--
-- Each cell has exactly one witness in this arc (extensible: future
-- arcs may add multiple witnesses per cell, in which case this
-- becomes a Vec-valued lookup).
--
-- The `Free-other` cell has NO witness in this arc — returned by
-- convention as the Lojban witness (placeholder); future arcs
-- adding witnesses fix this. Per [[feedback-comments-dont-overclaim]]
-- this is documented rather than overclaimed.
------------------------------------------------------------------------

witness-by-class : FreeConstructionClass → Lang
witness-by-class Free-monoid    = lojban
witness-by-class Free-F2-module = tokipona
witness-by-class Free-cyclic    = solresol
witness-by-class Free-relation  = kelen
witness-by-class Free-CCC       = lambda-lang
witness-by-class Free-Lie       = lie-lang
witness-by-class Free-other     = lojban  -- placeholder
