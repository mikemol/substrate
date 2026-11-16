------------------------------------------------------------------------
-- Substrate.TokiPona.AsFreeOverBasis.TokiponaFreeStructure
--
-- Defines: tokipona-free-structure
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.TokiPona.AsFreeOverBasis; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.AsFreeOverBasis.TokiponaFreeStructure where

open import Substrate.TokiPona.SemanticSpace
open import Substrate.TokiPona.Nimi
open import Substrate.TokiPona.NimiSpace
open import Substrate.Category.FreeOverBasis



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
