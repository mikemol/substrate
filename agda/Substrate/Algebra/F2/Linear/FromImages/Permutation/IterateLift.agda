------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.IterateLift
--
-- iterate-on-basis + basis-permutation-order-k: iteration of
-- basis-permutation-Linear at a basis vector tracks σ-iterate at
-- the index. The order-k generalization at the basis level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.IterateLift where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat.Nat

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.CompL
open import Substrate.Algebra.F2.Linear.CompLAssoc
open import Substrate.Algebra.F2.Linear.CompLIdentityL
open import Substrate.Algebra.F2.Linear.CompLIdentityR
open import Substrate.Algebra.F2.Linear.IdL
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.Preserves
open import Substrate.Category.Coalgebra.FiniteOrder using (iterate)

open import Substrate.Foundation.Fin.Iterate
  using (σ-iterate; HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Linear
  using (basis-permutation-Linear; apply-basis-permutation-Linear)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- iterate-on-basis:
--   iterate k (apply (basis-permutation-Linear σ)) (basis i)
--     ≡ basis (σ-iterate k σ i)

iterate-on-basis :
  ∀ {n} (σ : Fin n → Fin n) (k : ℕ) (i : Fin n) →
  iterate k (apply (basis-permutation-Linear σ)) (basis i)
    ≡ basis (σ-iterate k σ i)
iterate-on-basis σ zero    i = refl
iterate-on-basis σ (suc k) i =
  trans (cong (apply (basis-permutation-Linear σ)) (iterate-on-basis σ k i))
        (apply-basis-permutation-Linear σ (σ-iterate k σ i))

------------------------------------------------------------------------
-- basis-permutation-order-k: order-k generalization at the basis level.

basis-permutation-order-k :
  ∀ {n} (σ : Fin n → Fin n) (k : ℕ) →
  HasOrderPerm σ k →
  (i : Fin n) →
  iterate k (apply (basis-permutation-Linear σ)) (basis i) ≡ basis i
basis-permutation-order-k σ k order-witness i =
  trans (iterate-on-basis σ k i) (cong basis (order-witness i))
