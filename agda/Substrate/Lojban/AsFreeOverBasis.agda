------------------------------------------------------------------------
-- Substrate.Lojban.AsFreeOverBasis
--
-- C2 of the Categorical Linguistics Classification arc per
-- [[project-language-as-free-construction-classification]].
--
-- Retrofits Lojban L8 WordAlgebra as a FreeOverBasis instance in
-- the Free-monoid cell of the classification lattice. Thin adapter
-- — the substantive universal property (free-monoid extension)
-- already lives in Substrate.Lojban.WordAlgebra; this slice just
-- packages it.
--
-- Per [[feedback-coalgebraic-not-consumer-driven]] now-applied-
-- positively: with the parent primitive C1 in place, Lojban L8 is
-- coalgebraically rewritten as a FreeOverBasis instance without
-- modifying the original Lojban modules. The contrast is that the
-- L8 module is preserved as-is (gauge-honest); C2 is the witness
-- adapter.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.AsFreeOverBasis where

open import Substrate.Lojban.Gismu using (Gismu)
open import Substrate.Lojban.Word Gismu using (LojbanWord; single)
open import Substrate.Category.FreeOverBasis
  using (FreeOverBasis; mkFreeOverBasis;
         LanguageWitness; mkWitness;
         FreeConstructionClass; Free-monoid;
         WitnessName; Lojban)

------------------------------------------------------------------------
-- 1. The FreeOverBasis instance for Lojban.
--
-- Basis: Gismu (the vocabulary basis from L3).
-- Free carrier: LojbanWord (the Coxeter-Word-backed free monoid).
-- Unit: single — each gismu lifts to a one-symbol word.
--
-- The substantive universal property (free-monoid extension via
-- WordAlgebra.WithTarget; homomorphism law via WordAlgebra.extend-
-- merge) is unchanged from L8.
------------------------------------------------------------------------

lojban-free-structure : FreeOverBasis Gismu LojbanWord
lojban-free-structure = mkFreeOverBasis single

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
