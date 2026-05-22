------------------------------------------------------------------------
-- Substrate.Category.HC.ModelCategory
-- HC37 — Model category UP (cofibrations / fibrations / weak equivs).
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.ModelCategory where
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)
ModelCategory-UP : UPArrow
ModelCategory-UP = placeholder
