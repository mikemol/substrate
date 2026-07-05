------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Compose
--
-- Two commuting order-2 permutations compose to an order-2 permutation.
-- The Klein-four-group at the permutation level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Compose where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)

open import Substrate.Foundation.Fin.Iterate
  using (HasOrderPerm)

HasOrderPerm-compose-commute-order-2 :
  ∀ {n} (σ τ : Fin n → Fin n) →
  HasOrderPerm σ 2 → HasOrderPerm τ 2 →
  ((i : Fin n) → σ (τ i) ≡ τ (σ i)) →
  HasOrderPerm (λ x → σ (τ x)) 2
HasOrderPerm-compose-commute-order-2 σ τ σ-ord τ-ord commute i =
  trans (cong σ (sym (commute (τ i))))
  (trans (cong (λ z → σ (σ z)) (τ-ord i))
         (σ-ord i))
