------------------------------------------------------------------------
-- Substrate.Category.HC.InfYoneda
-- HC35 — ∞-Yoneda embedding よ∞ : C → PSh∞(C) statement.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.InfYoneda where
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)
InfYoneda-UP : UPArrow
InfYoneda-UP = placeholder
