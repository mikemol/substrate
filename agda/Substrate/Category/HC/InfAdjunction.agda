------------------------------------------------------------------------
-- Substrate.Category.HC.InfAdjunction
-- HC36 — Adjunction in a quasi-category (∞-adjoint pair) UP.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.InfAdjunction where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
InfAdjunction-UP : UPArrow
InfAdjunction-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
