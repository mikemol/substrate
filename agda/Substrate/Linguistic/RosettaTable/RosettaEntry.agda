------------------------------------------------------------------------
-- Substrate.Linguistic.RosettaTable.RosettaEntry
--
-- Defines: RosettaEntry, left, mkEntry, right, same-class
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RosettaTable; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RosettaTable.RosettaEntry where

open import Substrate.Category.FreeOverBasis
open import Substrate.Linguistic.Roster.BasisOf
open import Substrate.Linguistic.Roster.FreeCarrierOf
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
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 1. RosettaEntry: a row of the cross-language alignment table.
--
-- Records the pair of names, classes, and the same-class? flag.
-- The substrate-native ⊎-OR carries the YES / NO flag without
-- needing Bool: `here` = same class; `there` = different class.
-- left/right are Lang values now (⟡rc-lang, W5-L3) — the witness
-- itself is reached via `witness-of` where needed; RosettaEntry
-- drops to Set₀.
------------------------------------------------------------------------

record RosettaEntry : Set where
  constructor mkEntry
  field
    left       : Lang
    right      : Lang
    same-class : (class (witness-of left) ≡ class (witness-of right))
                   ⊎-OR (class (witness-of left) ≡ class (witness-of right) → ⊥)
