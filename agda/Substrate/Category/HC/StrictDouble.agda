------------------------------------------------------------------------
-- Substrate.Category.HC.StrictDouble
-- HC23 — Strict double category UP (no coherence-witness slack).
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.StrictDouble where
open import Substrate.Category.HC.PlaceholderUP using (placeholder; PlaceholderUPArrow)
StrictDouble-UP : PlaceholderUPArrow
StrictDouble-UP = placeholder
