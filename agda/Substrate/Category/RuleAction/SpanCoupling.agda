------------------------------------------------------------------------
-- Substrate.Category.RuleAction.SpanCoupling
--
-- Bifilar-reference factor: (rule-right, overlap-mask).
-- Subsumes B-frame bidirectional reference. Identity = no coupling.
-- This factor is NON-commutative; the SpanCoupling factor carries
-- the H-rung non-commutativity of RuleAction's product algebra.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction.SpanCoupling where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Bool using (Bool)
open import Substrate.Foundation.List using (List; [])
open import Substrate.Foundation.Maybe using (Maybe; nothing)

record SpanCoupling : Set where
  field
    rule-right   : Maybe ℕ
    overlap-mask : List Bool

open SpanCoupling public

identity-span : SpanCoupling
identity-span = record { rule-right = nothing ; overlap-mask = [] }
