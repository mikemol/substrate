------------------------------------------------------------------------
-- Substrate.Linguistic.Roster.FreeCarrierOf
--
-- Defines: FreeCarrier-of
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.Roster; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Roster.FreeCarrierOf where

open import Substrate.TokiPona.Nimi
open import Substrate.TokiPona.SemanticSpace
open import Substrate.Solresol.Fragment.Word
open import Substrate.Kelen.Fragment.KelenWord
open import Substrate.Lambda.Fragment.SKIWord
open import Substrate.Invented.LieFragment
open import Substrate.Linguistic.Roster.Lang
open import Substrate.Lojban.Gismu
open import Substrate.Lojban.Word Gismu



FreeCarrier-of : Lang → Set
FreeCarrier-of lojban      = LojbanWord
FreeCarrier-of tokipona    = SemVec nimi-count
FreeCarrier-of solresol    = SolresolWord
FreeCarrier-of kelen       = KelenWord
FreeCarrier-of lambda-lang = SKIWord
FreeCarrier-of lie-lang    = LieExpr
