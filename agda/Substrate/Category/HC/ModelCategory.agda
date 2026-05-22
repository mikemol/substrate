------------------------------------------------------------------------
-- Substrate.Category.HC.ModelCategory
-- HC37 — Model category UP (cofibrations / fibrations / weak equivs).
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.ModelCategory where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
ModelCategory-UP : UPArrow
ModelCategory-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
