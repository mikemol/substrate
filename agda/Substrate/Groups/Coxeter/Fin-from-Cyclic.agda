------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Fin-from-Cyclic
--
-- The bridge between Coxeter.Cyclic (Fin-indexed Canonical) and
-- Coxeter-Fin-Generic (single-index Canonical).
--
-- Path 2 Phase 3: any Coxeter.Cyclic n instance yields a complete
-- Coxeter-Fin chain at order (suc n). The per-Zₙ-Coxeter-Fin file's
-- bijection + action + order-witness data ALL come from Cyclic;
-- this module wraps them into Coxeter-Fin-Generic's signature.
--
-- Existential view: bundle the position index with the Canonical
-- value to recover the single-index `Canonical : Word Gen → Set`
-- shape the Generic expects.
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
-- Existential view of the Fin-indexed Canonical.
--
-- Canonical-ex w = there exists a position k such that Canonical w k.
-- This matches Coxeter-Fin-Generic's `Canonical : Word Gen → Set`
-- signature.
------------------------------------------------------------------------

Canonical-ex : Word Gen → Set
Canonical-ex w = Σ (Fin (suc n)) (Canonical w)

------------------------------------------------------------------------
-- Lifted insert-canonical to the existential view.
--
-- The Cyclic insert-canonical is at the indexed level; lift by
-- projecting + applying + repackaging with the σ-stepped position.
------------------------------------------------------------------------

insert-canonical-ex : (g : Gen) {w : Word Gen} →
                      Canonical-ex w → Canonical-ex (insert g w)
insert-canonical-ex g (k , c) = σ k , insert-canonical g c

------------------------------------------------------------------------
-- Bijection at the existential view.
------------------------------------------------------------------------

canonical-to-Fin-ex : ∀ {w} → Canonical-ex w → Fin (suc n)
canonical-to-Fin-ex (k , _) = k

Fin-to-canonical-ex : Fin (suc n) → Σ (Word Gen) Canonical-ex
Fin-to-canonical-ex k = power (toℕ k) , (k , c-here k)

------------------------------------------------------------------------
-- Action correspondence — trivial at the existential view.
--
-- canonical-to-Fin-ex (insert-canonical-ex a c) projects to σ k where
-- k = canonical-to-Fin-ex c. Refl.
------------------------------------------------------------------------

action-of-a-is-σ-ex : ∀ {w} (c : Canonical-ex w) →
                      canonical-to-Fin-ex (insert-canonical-ex a c)
                      ≡ σ (canonical-to-Fin-ex c)
action-of-a-is-σ-ex (k , _) = refl

------------------------------------------------------------------------
-- Apply Coxeter-Fin-Generic at order (suc n).
--
-- Every piece comes from Cyclic + the existential view. No per-Zₙ
-- enumeration anywhere — the chain materialises from the cyclic
-- structure parameter `n` alone.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter-Fin-Generic
  (suc n) Gen a Canonical-ex insert insert-canonical-ex
  canonical-to-Fin-ex Fin-to-canonical-ex σ
  action-of-a-is-σ-ex σ-HasOrderPerm
  public
