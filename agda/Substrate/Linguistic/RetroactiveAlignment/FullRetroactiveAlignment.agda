------------------------------------------------------------------------
-- Substrate.Linguistic.RetroactiveAlignment.FullRetroactiveAlignment
--
-- Defines: FullRetroactiveAlignment, kelen, lambda, lie, lojban, solresol, tokipona
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RetroactiveAlignment.FullRetroactiveAlignment where

open import Substrate.Category.FreeOverBasis
open import Substrate.Lojban.AsFreeOverBasis.LojbanWitness
open import Substrate.TokiPona.AsFreeOverBasis.TokiponaWitness
open import Substrate.Solresol.Fragment.Witness
open import Substrate.Kelen.Fragment.KelenWitness
open import Substrate.Lambda.Fragment.LambdaWitness
open import Substrate.Invented.LieFragment
open import Substrate.Foundation.Eq
open import Substrate.Linguistic.RetroactiveAlignment.WitnessAlignment



------------------------------------------------------------------------
-- 3. The aggregate record: all six witnesses aligned.
--
-- A single substrate-internal value certifying that the parent
-- primitive (FreeOverBasis from C1) covers all six witnesses with
-- their correct names + classifications.
------------------------------------------------------------------------

record FullRetroactiveAlignment : Set where
  field
    lojban   : WitnessAlignment lojban-witness
    tokipona : WitnessAlignment tokipona-witness
    solresol : WitnessAlignment solresol-witness
    kelen    : WitnessAlignment kelen-witness
    lambda   : WitnessAlignment lambda-witness
    lie      : WitnessAlignment lie-witness
