------------------------------------------------------------------------
-- Substrate.Category.HC.StrictDouble
-- HC23 — Strict double category UP (no coherence-witness slack).
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.StrictDouble where
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)
StrictDouble-UP : UPArrow
StrictDouble-UP = placeholder
