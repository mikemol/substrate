------------------------------------------------------------------------
-- Substrate.Category.HC.BraidedFunctor
-- HC13 — Braided functor: F preserving ⊗ and braiding β.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.BraidedFunctor where
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)
BraidedFunctor-UP : UPArrow
BraidedFunctor-UP = placeholder
