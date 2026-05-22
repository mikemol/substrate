------------------------------------------------------------------------
-- Substrate.Category.HC.DeltaCategory
-- HC32 — Δ category: finite ordinals + order-preserving maps.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.DeltaCategory where
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)
DeltaCategory-UP : UPArrow
DeltaCategory-UP = placeholder
