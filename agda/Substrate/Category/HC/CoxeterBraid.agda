------------------------------------------------------------------------
-- Substrate.Category.HC.CoxeterBraid
-- HC15 — Coxeter braid relations (sᵢsⱼ)ᵐ=e as a braiding instance UP.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.CoxeterBraid where
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)
CoxeterBraid-UP : UPArrow
CoxeterBraid-UP = placeholder
