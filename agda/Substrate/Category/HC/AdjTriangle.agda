------------------------------------------------------------------------
-- Substrate.Category.HC.AdjTriangle
--
-- HC6 of the higher-cat content arc per [scratch/up_topos_arc_plan.md].
--
-- Adjunction triangle identities UP: the unit/counit pair (η, ε)
-- of an adjunction F ⊣ G must satisfy the snake / triangle
-- identities (Gε ∘ ηG = id_G and εF ∘ Fη = id_F).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.HC.AdjTriangle where

open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)

AdjTriangle-UP : UPArrow
AdjTriangle-UP = placeholder
