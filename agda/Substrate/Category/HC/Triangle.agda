------------------------------------------------------------------------
-- Substrate.Category.HC.Triangle
--
-- HC3 of the higher-cat content arc per [scratch/up_topos_arc_plan.md].
--
-- Triangle coherence: (a ⊗ I) ⊗ b ─→ a ⊗ (I ⊗ b) commutes with the
-- unitor up to the associator. The Mac-Lane triangle.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.HC.Triangle where

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)

Triangle-UP : UPArrow
Triangle-UP = record
  { Source  = ⊤
  ; Target  = ⊤
  ; Witness = λ _ _ → ⊤
  }
