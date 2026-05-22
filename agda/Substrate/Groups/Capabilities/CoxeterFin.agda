------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.CoxeterFin
--
-- Tier 2 capability record for the Coxeter-Fin chain: packages the
-- parameters of Substrate.Groups.Coxeter-Fin-Generic as a record.
--
-- Each Zₙ with the capability supplies `cap-CoxeterFin : CoxeterFinCapability n`.
-- A missing field is a typecheck error rather than a missing module
-- (Tier 1's Manifest catches the latter; this record catches the
-- former).
--
-- The record + per-Zₙ witnesses form the Coxeter-Fin column of the
-- (Zₙ × Capability) cone. The Tier 3 reflective completeness theorem
-- (separate slice) consumes these witnesses uniformly.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Capabilities.CoxeterFin where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Product using (Σ)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Groups.Coxeter.Word using (Word)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation using (HasOrderPerm)

------------------------------------------------------------------------
-- The capability record. Fields correspond 1:1 to the parameters of
-- Substrate.Groups.Coxeter-Fin-Generic.
------------------------------------------------------------------------

record CoxeterFinCapability (n : ℕ) : Set₁ where
  field
    Gen               : Set
    a                 : Gen
    Canonical         : Word Gen → Set
    insert            : Gen → Word Gen → Word Gen
    insert-canonical  : (g : Gen) {w : Word Gen} →
                        Canonical w → Canonical (insert g w)
    canonical-to-Fin  : ∀ {w} → Canonical w → Fin n
    Fin-to-canonical  : Fin n → Σ (Word Gen) Canonical
    σ                 : Fin n → Fin n
    action-of-a-is-σ  : ∀ {w} (c : Canonical w) →
                        canonical-to-Fin (insert-canonical a c)
                        ≡ σ (canonical-to-Fin c)
    σ-aⁿ=ε            : HasOrderPerm σ n

------------------------------------------------------------------------
-- Z₂ witness.
------------------------------------------------------------------------

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z2-Coxeter-Fin as Z₂-Fin
import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle2 as Cycle₂

cap-Z₂ : CoxeterFinCapability 2
cap-Z₂ = record
  { Gen               = Z₂.Gen
  ; a                 = Z₂.a
  ; Canonical         = Z₂.Canonical
  ; insert            = Z₂.insert
  ; insert-canonical  = Z₂.insert-canonical
  ; canonical-to-Fin  = Z₂-Fin.canonical-to-Fin
  ; Fin-to-canonical  = Z₂-Fin.Fin-to-canonical
  ; σ                 = Cycle₂.σ₂
  ; action-of-a-is-σ  = Z₂-Fin.action-of-a-is-σ₂
  ; σ-aⁿ=ε            = Z₂-Fin.σ₂-HasOrderPerm-from-Z2-Coxeter
  }

------------------------------------------------------------------------
-- Z₃ witness.
------------------------------------------------------------------------

import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z3-Coxeter-Fin as Z₃-Fin
import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3 as Cycle₃

cap-Z₃ : CoxeterFinCapability 3
cap-Z₃ = record
  { Gen               = Z₃.Gen
  ; a                 = Z₃.a
  ; Canonical         = Z₃.Canonical
  ; insert            = Z₃.insert
  ; insert-canonical  = Z₃.insert-canonical
  ; canonical-to-Fin  = Z₃-Fin.canonical-to-Fin
  ; Fin-to-canonical  = Z₃-Fin.Fin-to-canonical
  ; σ                 = Cycle₃.σ₃
  ; action-of-a-is-σ  = Z₃-Fin.action-of-a-is-σ₃
  ; σ-aⁿ=ε            = Z₃-Fin.σ₃-HasOrderPerm-from-Z3-Coxeter
  }

------------------------------------------------------------------------
-- Z₄ witness.
------------------------------------------------------------------------

import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.Z4-Coxeter-Fin as Z₄-Fin
import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle4 as Cycle₄

cap-Z₄ : CoxeterFinCapability 4
cap-Z₄ = record
  { Gen               = Z₄.Gen
  ; a                 = Z₄.a
  ; Canonical         = Z₄.Canonical
  ; insert            = Z₄.insert
  ; insert-canonical  = Z₄.insert-canonical
  ; canonical-to-Fin  = Z₄-Fin.canonical-to-Fin
  ; Fin-to-canonical  = Z₄-Fin.Fin-to-canonical
  ; σ                 = Cycle₄.σ₄
  ; action-of-a-is-σ  = Z₄-Fin.action-of-a-is-σ₄
  ; σ-aⁿ=ε            = Z₄-Fin.σ₄-HasOrderPerm-from-Z4-Coxeter
  }

------------------------------------------------------------------------
-- Z₅ witness.
------------------------------------------------------------------------

import Substrate.Groups.Z5-Coxeter as Z₅
import Substrate.Groups.Z5-Coxeter-Fin as Z₅-Fin
import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle5 as Cycle₅

cap-Z₅ : CoxeterFinCapability 5
cap-Z₅ = record
  { Gen               = Z₅.Gen
  ; a                 = Z₅.a
  ; Canonical         = Z₅.Canonical
  ; insert            = Z₅.insert
  ; insert-canonical  = Z₅.insert-canonical
  ; canonical-to-Fin  = Z₅-Fin.canonical-to-Fin
  ; Fin-to-canonical  = Z₅-Fin.Fin-to-canonical
  ; σ                 = Cycle₅.σ₅
  ; action-of-a-is-σ  = Z₅-Fin.action-of-a-is-σ₅
  ; σ-aⁿ=ε            = Z₅-Fin.σ₅-HasOrderPerm-from-Z5-Coxeter
  }

------------------------------------------------------------------------
-- Z₇ witness.
------------------------------------------------------------------------

import Substrate.Groups.Z7-Coxeter as Z₇
import Substrate.Groups.Z7-Coxeter-Fin as Z₇-Fin
import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle7 as Cycle₇

cap-Z₇ : CoxeterFinCapability 7
cap-Z₇ = record
  { Gen               = Z₇.Gen
  ; a                 = Z₇.a
  ; Canonical         = Z₇.Canonical
  ; insert            = Z₇.insert
  ; insert-canonical  = Z₇.insert-canonical
  ; canonical-to-Fin  = Z₇-Fin.canonical-to-Fin
  ; Fin-to-canonical  = Z₇-Fin.Fin-to-canonical
  ; σ                 = Cycle₇.σ₇
  ; action-of-a-is-σ  = Z₇-Fin.action-of-a-is-σ₇
  ; σ-aⁿ=ε            = Z₇-Fin.σ₇-HasOrderPerm-from-Z7-Coxeter
  }
