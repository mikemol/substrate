------------------------------------------------------------------------
-- Substrate.Category.HC.SpanDouble
-- HC24 — Span double category: objects = sets, hor-1-cells = sets,
-- vert-1-cells = spans, squares = morphisms of spans.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.SpanDouble where
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)
SpanDouble-UP : UPArrow
SpanDouble-UP = placeholder
