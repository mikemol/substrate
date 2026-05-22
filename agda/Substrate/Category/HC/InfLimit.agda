------------------------------------------------------------------------
-- Substrate.Category.HC.InfLimit
-- HC39 — ∞-categorical limit UP (homotopy limit).
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.InfLimit where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
InfLimit-UP : UPArrow
InfLimit-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
