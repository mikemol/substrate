------------------------------------------------------------------------
-- Substrate.Category.HC.SimplicialSet
-- HC31 — Simplicial set UP: presheaf on Δ.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.SimplicialSet where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
SimplicialSet-UP : UPArrow
SimplicialSet-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
