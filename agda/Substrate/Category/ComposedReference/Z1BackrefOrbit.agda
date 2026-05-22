------------------------------------------------------------------------
-- Substrate.Category.ComposedReference.Z1BackrefOrbit
--
-- Z1-backref-orbit: classical LZ77-style backreference to recent
-- output. Identity action (no transformation), algebraic basis.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference.Z1BackrefOrbit where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Category.ComposedReference.EmissionSource using (EmissionSource; Recent)
open import Substrate.Category.ComposedReference.ActionAlgebra using (identity-action)
open import Substrate.Category.ComposedReference.BasisLabel using (BasisLabel; ALGEBRAIC)
open import Substrate.Category.ComposedReference.Record using (ComposedReference)

Z1-backref-orbit : ℕ → ℕ → ComposedReference
Z1-backref-orbit dist len = record
  { source = Recent
  ; distance = dist
  ; length = len
  ; action = identity-action
  ; basis = ALGEBRAIC
  }
