------------------------------------------------------------------------
-- Substrate.Category.HC.DeltaCategory
-- HC32 — Δ category: finite ordinals + order-preserving maps.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.DeltaCategory where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
DeltaCategory-UP : UPArrow
DeltaCategory-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
