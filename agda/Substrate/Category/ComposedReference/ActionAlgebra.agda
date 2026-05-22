------------------------------------------------------------------------
-- Substrate.Category.ComposedReference.ActionAlgebra
--
-- The action-algebra record carried by each emission: a V₄ residue
-- plus (start-phase, length-mask) affine projection slots. Mirrors
-- Substrate.Category.RuleAction's three sub-actions, here keeping
-- only the V₄ + affine factors active (F₂Patch / SpanCoupling
-- reserved for later composition).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference.ActionAlgebra where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Maybe using (Maybe; nothing)
open import Substrate.Category.ComposedReference.V4 using (V₄; e)

record ActionAlgebra : Set where
  field
    residue        : V₄
    start-phase    : ℕ
    length-mask    : Maybe ℕ

open ActionAlgebra public

identity-action : ActionAlgebra
identity-action = record
  { residue = e ; start-phase = 0 ; length-mask = nothing }
