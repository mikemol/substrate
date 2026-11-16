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

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)

open import Substrate.Groups.Coxeter.Word using (Word)
open import Substrate.Foundation.Eq
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
open import Substrate.Groups.Coxeter.Cyclic.Base.HasOrderPerm

module Substrate.Groups.Coxeter.Fin-from-Cyclic (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n using (Gen; power; c-here; a; σ; insert; σ-HasOrderPerm)
open import Substrate.Groups.Coxeter.Cyclic.Existential n using (Canonical-ex; insert-canonical-ex)
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

