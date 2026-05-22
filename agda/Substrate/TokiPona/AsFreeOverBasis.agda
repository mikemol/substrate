------------------------------------------------------------------------
-- Substrate.TokiPona.AsFreeOverBasis
--
-- C3 of the Categorical Linguistics Classification arc per
-- [[project-language-as-free-construction-classification]].
--
-- Sister to C2 (Lojban retrofit). Packages Toki Pona T8
-- LinearAlgebra as a FreeOverBasis instance in the Free-F2-module
-- cell of the classification lattice. Thin adapter — the universal
-- property (free-F₂-module extension via NimiFreeLinearization)
-- already lives in Substrate.TokiPona.LinearAlgebra.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.AsFreeOverBasis where

open import Substrate.TokiPona.SemanticSpace using (SemVec; basis)
open import Substrate.TokiPona.Nimi using (Nimi; nimi-count; nimi-index)
open import Substrate.TokiPona.NimiSpace using (nimi-as-vector)
open import Substrate.Category.FreeOverBasis
  using (FreeOverBasis; mkFreeOverBasis;
         LanguageWitness; mkWitness;
         FreeConstructionClass; Free-F2-module;
         WitnessName; TokiPona)

------------------------------------------------------------------------
-- 1. The FreeOverBasis instance for Toki Pona.
--
-- Basis: Nimi (the vocabulary basis from T2).
-- Free carrier: SemVec nimi-count (one-hot embedding into the F₂
-- vector space of dimension 32).
-- Unit: nimi-as-vector — each nimi lifts to its corresponding
-- basis vector.
--
-- The substantive universal property (linear extension from basis
-- via NimiFreeLinearization; basis-agreement + uniqueness) is
-- unchanged from T8.
------------------------------------------------------------------------

tokipona-free-structure : FreeOverBasis Nimi (SemVec nimi-count)
tokipona-free-structure = mkFreeOverBasis nimi-as-vector

------------------------------------------------------------------------
-- 2. The packaged LanguageWitness.
------------------------------------------------------------------------

tokipona-witness : LanguageWitness
tokipona-witness = mkWitness
  TokiPona
  Nimi
  (SemVec nimi-count)
  tokipona-free-structure
  Free-F2-module
