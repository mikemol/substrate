------------------------------------------------------------------------
-- Substrate.Category.HC.SquareCompose
-- HC22 — Square composition (horizontal + vertical) UP.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.SquareCompose where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
SquareCompose-UP : UPArrow
SquareCompose-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
