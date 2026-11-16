------------------------------------------------------------------------
-- Substrate.Linguistic.RosettaTable.RosettaLojbanTokipona
--
-- Defines: rosetta-lojban-tokipona
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RosettaTable; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RosettaTable.RosettaLojbanTokipona where

open import Substrate.Category.FreeOverBasis
open import Substrate.Linguistic.Roster.Lang
open import Substrate.Linguistic.Roster.WitnessOf
open import Substrate.Linguistic.Classification.AllWitnesses
open import Substrate.Linguistic.Classification.ClassCompwitnessByClass
open import Substrate.Linguistic.Classification.NameCompwitnessByName
open import Substrate.Linguistic.Classification.SumOR
open import Substrate.Linguistic.Classification.WitnessByClass
open import Substrate.Linguistic.Classification.WitnessByName
open import Substrate.Linguistic.Classification.WitnessCount
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Eq
open import Substrate.Linguistic.RosettaTable.RosettaEntry
open import Substrate.Linguistic.RosettaTable.PairEntry



------------------------------------------------------------------------
-- 4. Worked cross-language pair entries.
--
-- A handful of demonstrated alignments — the substrate-internal
-- witnesses of the cross-classification work. C10 will display
-- the full pairwise catalog.
------------------------------------------------------------------------


-- Lojban × Toki Pona: different cells (discrete word-algebra vs.
-- F₂-module). The original linguistic Rosetta pair.
rosetta-lojban-tokipona : RosettaEntry
rosetta-lojban-tokipona = pair-entry lojban tokipona
