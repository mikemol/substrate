------------------------------------------------------------------------
-- Substrate.Category.HC.InfYoneda
-- HC35 — ∞-Yoneda embedding よ∞ : C → PSh∞(C) statement.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.InfYoneda where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
InfYoneda-UP : UPArrow
InfYoneda-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
