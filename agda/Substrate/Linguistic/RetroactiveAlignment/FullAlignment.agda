------------------------------------------------------------------------
-- Substrate.Linguistic.RetroactiveAlignment.FullAlignment
--
-- Defines: full-alignment
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RetroactiveAlignment.FullAlignment where

open import Substrate.Category.FreeOverBasis
open import Substrate.Lojban.AsFreeOverBasis.LojbanWitness
open import Substrate.TokiPona.AsFreeOverBasis.TokiponaWitness
open import Substrate.Solresol.Fragment.Witness
open import Substrate.Kelen.Fragment.KelenWitness
open import Substrate.Lambda.Fragment.LambdaWitness
open import Substrate.Invented.LieFragment
open import Substrate.Foundation.Eq
open import Substrate.Linguistic.RetroactiveAlignment.LojbanAligned
open import Substrate.Linguistic.RetroactiveAlignment.TokiponaAligned
open import Substrate.Linguistic.RetroactiveAlignment.SolresolAligned
open import Substrate.Linguistic.RetroactiveAlignment.KelenAligned
open import Substrate.Linguistic.RetroactiveAlignment.LambdaAligned
open import Substrate.Linguistic.RetroactiveAlignment.LieAligned
open import Substrate.Linguistic.RetroactiveAlignment.FullRetroactiveAlignment



full-alignment : FullRetroactiveAlignment
full-alignment = record
  { lojban   = lojban-aligned
  ; tokipona = tokipona-aligned
  ; solresol = solresol-aligned
  ; kelen    = kelen-aligned
  ; lambda   = lambda-aligned
  ; lie      = lie-aligned
  }

------------------------------------------------------------------------
-- 4. Capstone.
--
-- `full-alignment` is the substrate-internal witness that the
-- parent primitive's coverage of all six witnesses is consistent
-- and complete (within the arc's scope). The "shared parent
-- extraction deferred" prose from Lojban L10 + Toki Pona T10 is
-- now superseded by this aggregate. D9 supplements with a
-- ClosureLog recording WHAT was closed in the D-arc.
------------------------------------------------------------------------
