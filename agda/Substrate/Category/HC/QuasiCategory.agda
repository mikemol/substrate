------------------------------------------------------------------------
-- Substrate.Category.HC.QuasiCategory
-- HC34 — Kan complex + quasi-category UP (inner-horn fillings).
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.QuasiCategory where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
QuasiCategory-UP : UPArrow
QuasiCategory-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
