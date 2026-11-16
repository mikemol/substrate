------------------------------------------------------------------------
-- Substrate.Category.ComposedReference.Aa2ResidueBackref
--
-- AA2-residue-backref: LZ77-style backreference carrying a V₄
-- residue transformation. Algebraic basis.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference.Aa2ResidueBackref where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Maybe using (nothing)
open import Substrate.Category.ComposedReference.EmissionSource using (EmissionSource; Recent)
open import Substrate.Category.ComposedReference.ActionAlgebra using (ActionAlgebra)
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Category.ComposedReference.BasisLabel using (BasisLabel; ALGEBRAIC)
open import Substrate.Category.ComposedReference.Record using (ComposedReference)
open import Substrate.Cocycles.KRule

AA2-residue-backref : ℕ → ℕ → V₄ → ComposedReference
AA2-residue-backref dist len σ = record
  { source = Recent
  ; distance = dist
  ; length = len
  ; action = record { residue = σ
                      ; start-phase = 0
                      ; length-mask = nothing }
  ; basis = ALGEBRAIC
  }
