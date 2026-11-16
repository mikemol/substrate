------------------------------------------------------------------------
-- Substrate.TokiPona.AsFreeOverBasis.TokiponaWitness
--
-- Defines: tokipona-witness
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.TokiPona.AsFreeOverBasis; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.AsFreeOverBasis.TokiponaWitness where

open import Substrate.TokiPona.SemanticSpace
open import Substrate.TokiPona.Nimi
open import Substrate.TokiPona.NimiSpace
open import Substrate.Category.FreeOverBasis
open import Substrate.TokiPona.AsFreeOverBasis.TokiponaFreeStructure



------------------------------------------------------------------------
-- 2. The packaged LanguageWitness.
------------------------------------------------------------------------

tokipona-witness : LanguageWitness Nimi (SemVec nimi-count)
tokipona-witness = mkWitness
  TokiPona
  tokipona-free-structure
  Free-F2-module
