------------------------------------------------------------------------
-- Substrate.Linguistic.RosettaTable.RosettaLojbanLambda
--
-- Defines: rosetta-lojban-lambda
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RosettaTable; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RosettaTable.RosettaLojbanLambda where

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



-- Lojban × Lambda: both CCC-shaped, but Lambda is PURE FCC while
-- Lojban approximates with n-ary morphism. Different cells in the
-- arc's lattice (Free-monoid vs Free-CCC) but structurally adjacent.
rosetta-lojban-lambda : RosettaEntry
rosetta-lojban-lambda = pair-entry lojban lambda-lang
