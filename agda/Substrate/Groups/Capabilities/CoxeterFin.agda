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
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Iterate
open import Substrate.Foundation.Product using (Σ)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Groups.Coxeter.Word using (Word)

------------------------------------------------------------------------
-- The capability record. Fields correspond 1:1 to the parameters of
-- Substrate.Groups.Coxeter-Fin-Generic.
------------------------------------------------------------------------

-- ⟡set1-paydown: parameterize Gen (the generator carrier) AND the
-- Canonical : Word Gen → Set family out of the record; both were `field`s
-- valued in Set, forcing the record to Set₁. With them as module parameters
-- the record lands in Set. Consumers write `CoxeterFinCapability Gen Canonical n`.
open import Substrate.Algebra.Nat.CyclicSuc using (cyclic-suc)
module _ (Gen : Set) (Canonical : Word Gen → Set) where

  record CoxeterFinCapability (n : ℕ) : Set where
    field
      a                 : Gen
      insert            : Gen → Word Gen → Word Gen
      insert-canonical  : (g : Gen) {w : Word Gen} →
                          Canonical w → Canonical (insert g w)
      canonical-to-Fin  : ∀ {w} → Canonical w → Fin n
      Fin-to-canonical  : Fin n → Σ (Word Gen) Canonical
      σ                 : Fin n → Fin n
      action-of-a-is-σ  : ∀ {w} (c : Canonical w) →
                          canonical-to-Fin (insert-canonical a c)
                          ≡ σ (canonical-to-Fin c)
      σ-aⁿ=ε            : OrderOf σ n

  ------------------------------------------------------------------------
  -- from-coxeter-fin-data: take a Zₙ-Coxeter's data + a Zₙ-Coxeter-Fin's
  -- bijection + action + σₙ-from-Cycleₙ, produce the capability record.
  ------------------------------------------------------------------------

  from-coxeter-fin-data :
    ∀ {n}
    (a : Gen)
    (insert : Gen → Word Gen → Word Gen)
    (insert-canonical : (g : Gen) {w : Word Gen} →
                        Canonical w → Canonical (insert g w))
    (canonical-to-Fin : ∀ {w} → Canonical w → Fin n)
    (Fin-to-canonical : Fin n → Σ (Word Gen) Canonical)
    (σ : Fin n → Fin n)
    (action-of-a-is-σ : ∀ {w} (c : Canonical w) →
                        canonical-to-Fin (insert-canonical a c) ≡ σ (canonical-to-Fin c))
    (σ-aⁿ=ε : OrderOf σ n) →
    CoxeterFinCapability n
  from-coxeter-fin-data a insert insert-can c-to-Fin Fin-to-c σ act ord =
    record
      { a                = a
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
