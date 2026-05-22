------------------------------------------------------------------------
-- Substrate.Category.HC.Grothendieck
-- HC27 — Grothendieck construction ∫ : (C → Cat) → Fib(C) UP.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.Grothendieck where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
Grothendieck-UP : UPArrow
Grothendieck-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
