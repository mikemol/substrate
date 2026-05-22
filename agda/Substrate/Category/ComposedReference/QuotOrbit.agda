------------------------------------------------------------------------
-- Substrate.Category.ComposedReference.QuotOrbit
--
-- QUOT-orbit: emission referencing an existing rule's body slice.
-- The distance field is reinterpreted as rule_id; phase indexes
-- into the rule body. Algebraic basis (substrate-aligned).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference.QuotOrbit where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Maybe using (nothing)
open import Substrate.Category.ComposedReference.EmissionSource using (EmissionSource; Rule)
open import Substrate.Category.ComposedReference.ActionAlgebra using (ActionAlgebra)
open import Substrate.Category.ComposedReference.V4 using (e)
open import Substrate.Category.ComposedReference.BasisLabel using (BasisLabel; ALGEBRAIC)
open import Substrate.Category.ComposedReference.Record using (ComposedReference)

QUOT-orbit : ℕ → ℕ → ℕ → ComposedReference
QUOT-orbit rule_id phase len = record
  { source = Rule
  ; distance = rule_id
  ; length = len
  ; action = record { residue = e
                      ; start-phase = phase
                      ; length-mask = nothing }
  ; basis = ALGEBRAIC
  }
