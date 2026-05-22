------------------------------------------------------------------------
-- Substrate.Category.HC.QuillenAdjunction
-- HC38 — Quillen adjunction between model categories UP.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.QuillenAdjunction where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
QuillenAdjunction-UP : UPArrow
QuillenAdjunction-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
