------------------------------------------------------------------------
-- Substrate.Linguistic.Classification.AllWitnesses
--
-- Defines: all-witnesses
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.Classification; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Classification.AllWitnesses where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Linguistic.Roster.Lang
open import Substrate.Linguistic.Classification.WitnessCount



all-witnesses : Vec Lang witness-count
all-witnesses =
  lojban      ∷
  tokipona    ∷
  solresol    ∷
  kelen       ∷
  lambda-lang ∷
  lie-lang    ∷
  []
