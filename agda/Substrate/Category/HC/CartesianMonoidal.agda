------------------------------------------------------------------------
-- Substrate.Category.HC.CartesianMonoidal
-- HC18 — Cartesian-monoidal: ⊗ = product, I = terminal.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.CartesianMonoidal where
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)
CartesianMonoidal-UP : UPArrow
CartesianMonoidal-UP = placeholder
