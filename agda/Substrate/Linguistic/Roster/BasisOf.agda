------------------------------------------------------------------------
-- Substrate.Linguistic.Roster.BasisOf
--
-- Defines: Basis-of
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.Roster; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Roster.BasisOf where

open import Substrate.Lojban.Gismu
open import Substrate.TokiPona.Nimi
open import Substrate.Solresol.Fragment.Note
open import Substrate.Kelen.Fragment.Relational
open import Substrate.Lambda.Fragment.Combinator
open import Substrate.Invented.LieFragment
open import Substrate.Linguistic.Roster.Lang



------------------------------------------------------------------------
-- 2. Decode families: each Lang value's concrete Basis/FreeCarrier.
------------------------------------------------------------------------

Basis-of : Lang → Set
Basis-of lojban      = Gismu
Basis-of tokipona    = Nimi
Basis-of solresol    = Note
Basis-of kelen       = Relational
Basis-of lambda-lang = Combinator
Basis-of lie-lang    = LieGen
