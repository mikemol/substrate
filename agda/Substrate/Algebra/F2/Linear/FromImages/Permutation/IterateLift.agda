------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.IterateLift
--
-- iterate-on-basis + basis-permutation-order-k: iteration of
-- basis-permutation-Linear at a basis vector tracks σ-iterate at
-- the index. The order-k generalization at the basis level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.IterateLift where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Category.Coalgebra.FiniteOrder using (iterate)

open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Iterate
  using (σ-iterate; HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Linear
  using (basis-permutation-Linear; apply-basis-permutation-Linear)

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
