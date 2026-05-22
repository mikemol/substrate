------------------------------------------------------------------------
-- Substrate.Category.HC.Fibered
-- HC25 — Fibered category (cleavage) UP.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.Fibered where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
Fibered-UP : UPArrow
Fibered-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
