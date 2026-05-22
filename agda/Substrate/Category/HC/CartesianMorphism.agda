------------------------------------------------------------------------
-- Substrate.Category.HC.CartesianMorphism
-- HC26 — Cartesian morphism in a fibered category UP.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.CartesianMorphism where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
CartesianMorphism-UP : UPArrow
CartesianMorphism-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
