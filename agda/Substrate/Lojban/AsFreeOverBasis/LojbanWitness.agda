------------------------------------------------------------------------
-- Substrate.Lojban.AsFreeOverBasis.LojbanWitness
--
-- Defines: lojban-witness
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lojban.AsFreeOverBasis; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.AsFreeOverBasis.LojbanWitness where

open import Substrate.Lojban.Gismu
open import Substrate.Lojban.Word Gismu
open import Substrate.Category.FreeOverBasis
open import Substrate.Lojban.AsFreeOverBasis.LojbanFreeStructure



------------------------------------------------------------------------
-- 2. The packaged LanguageWitness.
--
-- Bundles the FreeOverBasis with the WitnessName + classification.
-- C8 (Classification) consumes this to populate the lattice.
------------------------------------------------------------------------

lojban-witness : LanguageWitness Gismu LojbanWord
lojban-witness = mkWitness
  Lojban
  lojban-free-structure
  Free-monoid
