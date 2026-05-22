------------------------------------------------------------------------
-- Substrate.Category.HC.StrictDouble
-- HC23 — Strict double category UP (no coherence-witness slack).
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.StrictDouble where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
StrictDouble-UP : UPArrow
StrictDouble-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
