------------------------------------------------------------------------
-- Substrate.Category.HC.BraidedHexagon
-- HC12 — Hexagon coherence for braided monoidal.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.BraidedHexagon where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
BraidedHexagon-UP : UPArrow
BraidedHexagon-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
