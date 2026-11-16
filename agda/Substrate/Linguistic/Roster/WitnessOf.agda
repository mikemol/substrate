------------------------------------------------------------------------
-- Substrate.Linguistic.Roster.WitnessOf
--
-- Defines: witness-of
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.Roster; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Roster.WitnessOf where

open import Substrate.Category.FreeOverBasis
open import Substrate.Lojban.Gismu
open import Substrate.Lojban.Word Gismu
open import Substrate.Lojban.AsFreeOverBasis.LojbanWitness
open import Substrate.TokiPona.Nimi
open import Substrate.TokiPona.SemanticSpace
open import Substrate.TokiPona.AsFreeOverBasis.TokiponaWitness
open import Substrate.Solresol.Fragment.Note
open import Substrate.Solresol.Fragment.Word
open import Substrate.Solresol.Fragment.Witness
open import Substrate.Kelen.Fragment.KelenWitness
open import Substrate.Kelen.Fragment.KelenWord
open import Substrate.Kelen.Fragment.Relational
open import Substrate.Lambda.Fragment.Combinator
open import Substrate.Lambda.Fragment.LambdaWitness
open import Substrate.Lambda.Fragment.SKIWord
open import Substrate.Invented.LieFragment
open import Substrate.Linguistic.Roster.Lang
open import Substrate.Linguistic.Roster.BasisOf
open import Substrate.Linguistic.Roster.FreeCarrierOf



------------------------------------------------------------------------
-- 3. witness-of: the decode to the packaged LanguageWitness.
------------------------------------------------------------------------

witness-of : (l : Lang) → LanguageWitness (Basis-of l) (FreeCarrier-of l)
witness-of lojban      = lojban-witness
witness-of tokipona    = tokipona-witness
witness-of solresol    = solresol-witness
witness-of kelen       = kelen-witness
witness-of lambda-lang = lambda-witness
witness-of lie-lang    = lie-witness
