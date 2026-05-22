------------------------------------------------------------------------
-- Substrate.Category.ComposedReference.IdentityEmission
--
-- identity-emission: the monoid identity at the codec emission layer.
-- Zero-length Recent reference with identity action and algebraic basis.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference.IdentityEmission where

open import Substrate.Category.ComposedReference.EmissionSource using (EmissionSource; Recent)
open import Substrate.Category.ComposedReference.ActionAlgebra using (identity-action)
open import Substrate.Category.ComposedReference.BasisLabel using (BasisLabel; ALGEBRAIC)
open import Substrate.Category.ComposedReference.Record using (ComposedReference)

identity-emission : ComposedReference
identity-emission = record
  { source = Recent
  ; distance = 0
  ; length = 0
  ; action = identity-action
  ; basis = ALGEBRAIC
  }
