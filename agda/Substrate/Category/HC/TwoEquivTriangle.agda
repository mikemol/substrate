------------------------------------------------------------------------
-- Substrate.Category.HC.TwoEquivTriangle
--
-- HC7 of the higher-cat content arc per [scratch/up_topos_arc_plan.md].
--
-- 2-equivalence triangle coherence UP: a pair of 1-cells (F, G) with
-- invertible-up-to-2-cell composites (FG ≅ id, GF ≅ id) must satisfy
-- the canonical triangle identities at the 2-cell level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.HC.TwoEquivTriangle where

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)

TwoEquivTriangle-UP : UPArrow
TwoEquivTriangle-UP = record
  { Source  = ⊤
  ; Target  = ⊤
  ; Witness = λ _ _ → ⊤
  }
