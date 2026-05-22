------------------------------------------------------------------------
-- Substrate.Category.ComposedReference.Aa6AffineBackref
--
-- AA6-affine-backref: LZ77-style backreference carrying a phase-shift
-- (affine projection) — identity residue + nontrivial start-phase.
-- Algebraic basis.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference.Aa6AffineBackref where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Maybe using (nothing)
open import Substrate.Category.ComposedReference.EmissionSource using (EmissionSource; Recent)
open import Substrate.Category.ComposedReference.ActionAlgebra using (ActionAlgebra)
open import Substrate.Category.ComposedReference.V4 using (e)
open import Substrate.Category.ComposedReference.BasisLabel using (BasisLabel; ALGEBRAIC)
open import Substrate.Category.ComposedReference.Record using (ComposedReference)

AA6-affine-backref : ℕ → ℕ → ℕ → ComposedReference
AA6-affine-backref dist len phase = record
  { source = Recent
  ; distance = dist
  ; length = len
  ; action = record { residue = e
                      ; start-phase = phase
                      ; length-mask = nothing }
  ; basis = ALGEBRAIC
  }
