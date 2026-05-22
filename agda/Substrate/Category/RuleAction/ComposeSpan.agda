------------------------------------------------------------------------
-- Substrate.Category.RuleAction.ComposeSpan
--
-- compose-span : the non-commutative SpanCoupling composition.
-- The FIRST non-trivial coupling wins (matches Python's
-- `a.span_coupling or b.span_coupling`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction.ComposeSpan where

open import Substrate.Foundation.Maybe using (just; nothing)
open import Substrate.Category.RuleAction.SpanCoupling
  using (SpanCoupling; rule-right)

compose-span : SpanCoupling → SpanCoupling → SpanCoupling
compose-span s₁ s₂ with rule-right s₁
... | just _  = s₁
... | nothing = s₂
