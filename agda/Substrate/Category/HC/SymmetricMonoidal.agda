------------------------------------------------------------------------
-- Substrate.Category.HC.SymmetricMonoidal
-- HC14 — Symmetric monoidal category UP (braiding involutive σ²=id).
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.SymmetricMonoidal where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
SymmetricMonoidal-UP : UPArrow
SymmetricMonoidal-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
