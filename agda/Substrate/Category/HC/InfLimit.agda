------------------------------------------------------------------------
-- Substrate.Category.HC.InfLimit
-- HC39 — ∞-categorical limit UP (homotopy limit).
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.InfLimit where
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)
InfLimit-UP : UPArrow
InfLimit-UP = placeholder
