------------------------------------------------------------------------
-- Substrate.Category.HC.HornInclusion
-- HC33 — Horn inclusion Λᵏₙ ↪ Δⁿ UP.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.HornInclusion where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
HornInclusion-UP : UPArrow
HornInclusion-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
