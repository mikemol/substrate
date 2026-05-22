------------------------------------------------------------------------
-- Substrate.Category.HC.Grothendieck
-- HC27 — Grothendieck construction ∫ : (C → Cat) → Fib(C) UP.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.Grothendieck where
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)
Grothendieck-UP : UPArrow
Grothendieck-UP = placeholder
