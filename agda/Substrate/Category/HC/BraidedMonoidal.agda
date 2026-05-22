------------------------------------------------------------------------
-- Substrate.Category.HC.BraidedMonoidal
-- HC11 — Braided monoidal category UP.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.BraidedMonoidal where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
BraidedMonoidal-UP : UPArrow
BraidedMonoidal-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
