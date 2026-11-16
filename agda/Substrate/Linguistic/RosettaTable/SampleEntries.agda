------------------------------------------------------------------------
-- Substrate.Linguistic.RosettaTable.SampleEntries
--
-- Defines: sample-entries
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RosettaTable; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RosettaTable.SampleEntries where

open import Substrate.Foundation.Vec
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
open import Substrate.Linguistic.RosettaTable.RosettaLojbanTokipona
open import Substrate.Linguistic.RosettaTable.RosettaLojbanLambda
open import Substrate.Linguistic.RosettaTable.RosettaTokiponaSolresol
open import Substrate.Linguistic.RosettaTable.RosettaKelenLambda
open import Substrate.Linguistic.RosettaTable.RosettaLojbanLojban



------------------------------------------------------------------------
-- 5. Sample cross-table.
--
-- A short Vec of representative entries demonstrating that the
-- generator works across all combinations. C10 expands this.
------------------------------------------------------------------------

sample-entries : Vec RosettaEntry 5
sample-entries =
  rosetta-lojban-tokipona     ∷
  rosetta-lojban-lambda       ∷
  rosetta-tokipona-solresol   ∷
  rosetta-kelen-lambda        ∷
  rosetta-lojban-lojban       ∷
  []
