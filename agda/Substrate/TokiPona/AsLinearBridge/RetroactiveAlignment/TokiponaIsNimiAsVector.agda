------------------------------------------------------------------------
-- Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment.TokiponaIsNimiAsVector
--
-- Defines: tokipona-η-is-nimi-as-vector
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment.TokiponaIsNimiAsVector where

open import Substrate.TokiPona.Nimi
open import Substrate.TokiPona.NimiSpace
open import Substrate.TokiPona.AsFreeOverBasis.TokiponaFreeStructure
open import Substrate.Category.FreeOverBasis
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 1. η of the TokiPona FreeOverBasis IS the `nimi-as-vector`
-- one-hot embedding.
--
-- Connects the Classification arc's basis embedding to the T1
-- SemanticSpace basis (each nimi → its corresponding basis vector
-- in SemVec nimi-count).
------------------------------------------------------------------------

tokipona-η-is-nimi-as-vector :
  (n : Nimi) → η tokipona-free-structure n ≡ nimi-as-vector n
tokipona-η-is-nimi-as-vector _ = refl
