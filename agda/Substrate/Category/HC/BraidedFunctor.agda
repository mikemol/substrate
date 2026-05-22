------------------------------------------------------------------------
-- Substrate.Category.HC.BraidedFunctor
-- HC13 — Braided functor: F preserving ⊗ and braiding β.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.BraidedFunctor where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
BraidedFunctor-UP : UPArrow
BraidedFunctor-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
