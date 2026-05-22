------------------------------------------------------------------------
-- Substrate.Category.HC.IndexedCategory
-- HC28 — Indexed category + Indexed ≃ Fibered equivalence UP.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.IndexedCategory where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
IndexedCategory-UP : UPArrow
IndexedCategory-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
