------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.CoxeterFin
--
-- Tier 2 capability record for the Coxeter-Fin chain: packages the
-- parameters of Substrate.Groups.Coxeter-Fin-Generic as a record.
--
-- `from-coxeter-fin-data` is the shared shape; per-Zₙ witnesses are
-- one-line applications.
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
-- from-coxeter-fin-data: take a Zₙ-Coxeter's data + a Zₙ-Coxeter-Fin's
-- bijection + action + σₙ-from-Cycleₙ, produce the capability record.
------------------------------------------------------------------------

from-coxeter-fin-data :
  ∀ {n}
  (Gen : Set) (a : Gen) (Canonical : Word Gen → Set)
  (insert : Gen → Word Gen → Word Gen)
  (insert-canonical : (g : Gen) {w : Word Gen} →
                      Canonical w → Canonical (insert g w))
  (canonical-to-Fin : ∀ {w} → Canonical w → Fin n)
  (Fin-to-canonical : Fin n → Σ (Word Gen) Canonical)
  (σ : Fin n → Fin n)
  (action-of-a-is-σ : ∀ {w} (c : Canonical w) →
                      canonical-to-Fin (insert-canonical a c) ≡ σ (canonical-to-Fin c))
  (σ-aⁿ=ε : HasOrderPerm σ n) →
  CoxeterFinCapability n
from-coxeter-fin-data Gen a Can insert insert-can c-to-Fin Fin-to-c σ act ord =
  record
    { Gen              = Gen
    ; a                = a
    ; Canonical        = Can
    ; insert           = insert
    ; insert-canonical = insert-can
    ; canonical-to-Fin = c-to-Fin
    ; Fin-to-canonical = Fin-to-c
    ; σ                = σ
    ; action-of-a-is-σ = act
    ; σ-aⁿ=ε           = ord
    }

------------------------------------------------------------------------
-- Per-Zₙ witnesses, one application each.
------------------------------------------------------------------------

-- Ⓖ.cyclen-collapse: the per-n Cycleₙ orbit-modules (thin renamings σₙ = cyclic-suc {n-1})
-- are obsolete — the cyclic permutation is the generic GENERATOR `cyclic-suc` directly, with n
-- inferred from each capability's index (the [[expose-generator-not-orbit]] collapse, finished).
open import Substrate.Algebra.Nat.CyclicSuc using (cyclic-suc)

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z2-Coxeter-Fin as Z₂-Fin

cap-Z₂ : CoxeterFinCapability 2
cap-Z₂ = from-coxeter-fin-data
  Z₂.Gen Z₂.a Z₂.Canonical Z₂.insert Z₂.insert-canonical
  Z₂-Fin.canonical-to-Fin Z₂-Fin.Fin-to-canonical
  cyclic-suc Z₂-Fin.action-of-a-is-σ₂
  Z₂-Fin.σ₂-HasOrderPerm-from-Z2-Coxeter

import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z3-Coxeter-Fin as Z₃-Fin

cap-Z₃ : CoxeterFinCapability 3
cap-Z₃ = from-coxeter-fin-data
  Z₃.Gen Z₃.a Z₃.Canonical Z₃.insert Z₃.insert-canonical
  Z₃-Fin.canonical-to-Fin Z₃-Fin.Fin-to-canonical
  cyclic-suc Z₃-Fin.action-of-a-is-σ₃
  Z₃-Fin.σ₃-HasOrderPerm-from-Z3-Coxeter

import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.Z4-Coxeter-Fin as Z₄-Fin

cap-Z₄ : CoxeterFinCapability 4
cap-Z₄ = from-coxeter-fin-data
  Z₄.Gen Z₄.a Z₄.Canonical Z₄.insert Z₄.insert-canonical
  Z₄-Fin.canonical-to-Fin Z₄-Fin.Fin-to-canonical
  cyclic-suc Z₄-Fin.action-of-a-is-σ₄
  Z₄-Fin.σ₄-HasOrderPerm-from-Z4-Coxeter

import Substrate.Groups.Z5-Coxeter as Z₅
import Substrate.Groups.Z5-Coxeter-Fin as Z₅-Fin

cap-Z₅ : CoxeterFinCapability 5
cap-Z₅ = from-coxeter-fin-data
  Z₅.Gen Z₅.a Z₅.Canonical Z₅.insert Z₅.insert-canonical
  Z₅-Fin.canonical-to-Fin Z₅-Fin.Fin-to-canonical
  cyclic-suc Z₅-Fin.action-of-a-is-σ₅
  Z₅-Fin.σ₅-HasOrderPerm-from-Z5-Coxeter

import Substrate.Groups.Z7-Coxeter as Z₇
import Substrate.Groups.Z7-Coxeter-Fin as Z₇-Fin

cap-Z₇ : CoxeterFinCapability 7
cap-Z₇ = from-coxeter-fin-data
  Z₇.Gen Z₇.a Z₇.Canonical Z₇.insert Z₇.insert-canonical
  Z₇-Fin.canonical-to-Fin Z₇-Fin.Fin-to-canonical
  cyclic-suc Z₇-Fin.action-of-a-is-σ₇
  Z₇-Fin.σ₇-HasOrderPerm-from-Z7-Coxeter
