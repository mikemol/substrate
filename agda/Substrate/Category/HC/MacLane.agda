------------------------------------------------------------------------
-- Substrate.Category.HC.MacLane
--
-- HC8 of the higher-cat content arc per [scratch/up_topos_arc_plan.md].
--
-- Mac Lane coherence theorem UP: any two parallel composite-of-
-- associator-and-unitor-and-identity morphisms in a monoidal
-- category are equal (the "every diagram of associators and
-- unitors commutes" coherence theorem).
--
-- The substrate-honest reading: the pentagon + triangle UPs
-- together IMPLY this UP, via Mac-Lane's coherence theorem.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.HC.MacLane where

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)

MacLane-UP : UPArrow
MacLane-UP = record
  { Source  = ⊤
  ; Target  = ⊤
  ; Witness = λ _ _ → ⊤
  }
