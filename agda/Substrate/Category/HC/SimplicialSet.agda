------------------------------------------------------------------------
-- Substrate.Category.HC.SimplicialSet
-- HC31 — Simplicial set UP: presheaf on Δ.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.SimplicialSet where
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)
SimplicialSet-UP : UPArrow
SimplicialSet-UP = placeholder
