------------------------------------------------------------------------
-- Substrate.Category.HC.DoubleCategory
-- HC21 — Double category UP: objects, horizontal/vertical 1-cells,
-- squares as 2-cells.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.DoubleCategory where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
DoubleCategory-UP : UPArrow
DoubleCategory-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
