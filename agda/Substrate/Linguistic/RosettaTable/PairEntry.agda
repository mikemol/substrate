------------------------------------------------------------------------
-- Substrate.Linguistic.RosettaTable.PairEntry
--
-- Defines: pair-entry
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RosettaTable; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RosettaTable.PairEntry where

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
open import Substrate.Linguistic.RosettaTable.ClassDecide



------------------------------------------------------------------------
-- 3. Pairwise RosettaEntry constructor.
--
-- Build a Rosetta entry for any two witnesses. The same-class flag
-- is decided by class-decide.
------------------------------------------------------------------------

pair-entry : (left right : Lang) → RosettaEntry
pair-entry l r = mkEntry l r (class-decide (class (witness-of l)) (class (witness-of r)))
