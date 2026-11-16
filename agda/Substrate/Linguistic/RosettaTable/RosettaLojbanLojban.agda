------------------------------------------------------------------------
-- Substrate.Linguistic.RosettaTable.RosettaLojbanLojban
--
-- Defines: rosetta-lojban-lojban
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RosettaTable; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RosettaTable.RosettaLojbanLojban where

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



-- Lojban × Lojban: trivial same-class diagonal entry.
rosetta-lojban-lojban : RosettaEntry
rosetta-lojban-lojban = pair-entry lojban lojban
