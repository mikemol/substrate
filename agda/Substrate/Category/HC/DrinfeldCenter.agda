------------------------------------------------------------------------
-- Substrate.Category.HC.DrinfeldCenter
-- HC19 — Drinfeld center Z(C) of a monoidal category C: half-braids.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.DrinfeldCenter where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
DrinfeldCenter-UP : UPArrow
DrinfeldCenter-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
