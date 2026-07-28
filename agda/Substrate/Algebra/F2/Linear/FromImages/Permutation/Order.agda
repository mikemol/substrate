------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Order
--
-- L-iterate + iterate-apply-as-L-iterate + HasOrder-from-perm +
-- HasOrderPerm-multiple-Linear: lift permutation order to Linear
-- order via linear-extensionality.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Order where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_*_ to _ℕ*_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Category.Coalgebra.FiniteOrder
  using (iterate; HasOrder; HasOrder-multiple)

open import Substrate.Foundation.Fin.Iterate
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Linear
  using (basis-permutation-Linear)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.IterateLift
  using (basis-permutation-order-k)

------------------------------------------------------------------------
-- L-iterate k L = L ∘L L ∘L ... ∘L L (k times, with id-L at k=0).

L-iterate : ∀ {n} → ℕ → Linear n n → Linear n n
L-iterate zero    L = id-L
L-iterate (suc k) L = L ∘L L-iterate k L

iterate-apply-as-L-iterate :
  ∀ {n} (L : Linear n n) (k : ℕ) (v : Vector n) →
  iterate k (apply L) v ≡ apply (L-iterate k L) v
iterate-apply-as-L-iterate L zero    v = refl
iterate-apply-as-L-iterate L (suc k) v =
  cong (apply L) (iterate-apply-as-L-iterate L k v)

------------------------------------------------------------------------
-- HasOrder-from-perm — lift permutation order to Linear order.

HasOrder-from-perm :
  ∀ {n} (σ : Fin n → Fin n) (k : ℕ) →
  HasOrderPerm σ k →
  HasOrder (apply (basis-permutation-Linear σ)) k
HasOrder-from-perm {n} σ k order-witness v =
  trans (iterate-apply-as-L-iterate (basis-permutation-Linear σ) k v)
        (linear-extensionality
          (L-iterate k (basis-permutation-Linear σ))
          id-L
          basis-agreement
          v)
  where
    L = basis-permutation-Linear σ

    basis-agreement :
      (i : Fin n) → apply (L-iterate k L) (basis i) ≡ apply id-L (basis i)
    basis-agreement i =
      trans (sym (iterate-apply-as-L-iterate L k (basis i)))
            (basis-permutation-order-k σ k order-witness i)

------------------------------------------------------------------------
-- HasOrderPerm-multiple-Linear — bundle HasOrder-from-perm with
-- HasOrder-multiple.

HasOrderPerm-multiple-Linear :
  ∀ {n} (σ : Fin n → Fin n) (k m : ℕ) →
  HasOrderPerm σ k →
  HasOrder (apply (basis-permutation-Linear σ)) (m ℕ* k)
HasOrderPerm-multiple-Linear σ k m hyp =
  HasOrder-multiple {γ = apply (basis-permutation-Linear σ)} {k = k}
                    (HasOrder-from-perm σ k hyp) m
