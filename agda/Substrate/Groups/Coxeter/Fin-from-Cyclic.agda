------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Fin-from-Cyclic
--
-- Apply Coxeter-Fin-Generic with Coxeter.Cyclic n's exports.
-- Cyclic now provides Canonical-ex + insert-canonical-ex directly,
-- so this module is a thin wrapper that:
--   (1) supplies the Fin-bijection helpers (canonical-to-Fin / Fin-to-canonical)
--   (2) applies Coxeter-Fin-Generic with the existential view
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin; toℕ)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Groups.Coxeter.Word using (Word)

module Substrate.Groups.Coxeter.Fin-from-Cyclic (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic n public

------------------------------------------------------------------------
-- Bijection helpers at the existential view.
------------------------------------------------------------------------

canonical-to-Fin-ex : ∀ {w} → Canonical-ex w → Fin (suc n)
canonical-to-Fin-ex (k , _) = k

Fin-to-canonical-ex : Fin (suc n) → Σ (Word Gen) Canonical-ex
Fin-to-canonical-ex k = power (toℕ k) , (k , c-here k)

action-of-a-is-σ-ex : ∀ {w} (c : Canonical-ex w) →
                      canonical-to-Fin-ex (insert-canonical-ex a c)
                      ≡ σ (canonical-to-Fin-ex c)
action-of-a-is-σ-ex (k , _) = refl

------------------------------------------------------------------------
-- Apply Coxeter-Fin-Generic at order (suc n).
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter-Fin-Generic
  (suc n) Gen a Canonical-ex insert insert-canonical-ex
  canonical-to-Fin-ex Fin-to-canonical-ex σ
  action-of-a-is-σ-ex σ-HasOrderPerm
  public
