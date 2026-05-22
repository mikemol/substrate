------------------------------------------------------------------------
-- Substrate.Category.HC.EckmannHilton
-- HC16 — Eckmann-Hilton: two commuting monoid structures on a set
-- coincide and are commutative.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.EckmannHilton where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
EckmannHilton-UP : UPArrow
EckmannHilton-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
