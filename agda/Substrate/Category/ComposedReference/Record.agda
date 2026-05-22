------------------------------------------------------------------------
-- Substrate.Category.ComposedReference.Record
--
-- The unified ComposedReference record itself: one opcode emission
-- carrying five composable fields (source, distance, length, action,
-- basis). The codec's match-search ranges over the product space;
-- decoder reads payload and applies each axis's transformation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference.Record where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Category.ComposedReference.EmissionSource using (EmissionSource)
open import Substrate.Category.ComposedReference.ActionAlgebra using (ActionAlgebra)
open import Substrate.Category.ComposedReference.BasisLabel using (BasisLabel)

record ComposedReference : Set where
  field
    source       : EmissionSource
    distance     : ℕ
    length       : ℕ
    action       : ActionAlgebra
    basis        : BasisLabel

open ComposedReference public
