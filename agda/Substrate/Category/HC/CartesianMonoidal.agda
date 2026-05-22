------------------------------------------------------------------------
-- Substrate.Category.HC.CartesianMonoidal
-- HC18 — Cartesian-monoidal: ⊗ = product, I = terminal.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.CartesianMonoidal where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
CartesianMonoidal-UP : UPArrow
CartesianMonoidal-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
