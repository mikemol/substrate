------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Iterate
--
-- σ-iterate, HasOrderPerm, σ-iterate-add, HasOrderPerm-multiple.
-- Foundational data for order-k basis-permutation work.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Iterate where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_+_ to _ℕ+_; _*_ to _ℕ*_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)

------------------------------------------------------------------------
-- σ-iterate k σ = σ ∘ σ ∘ ⋯ ∘ σ  (k times).

σ-iterate : ∀ {n} → ℕ → (Fin n → Fin n) → (Fin n → Fin n)
σ-iterate zero    σ = λ i → i
σ-iterate (suc k) σ = λ i → σ (σ-iterate k σ i)

------------------------------------------------------------------------
-- HasOrderPerm σ k = ∀ i → σ-iterate k σ i ≡ i  (pointwise σ^k = id).

HasOrderPerm : ∀ {n} → (Fin n → Fin n) → ℕ → Set
HasOrderPerm σ k = ∀ i → σ-iterate k σ i ≡ i

------------------------------------------------------------------------
-- σ-iterate-add — additivity of iteration in the count.
--   σ-iterate (a + b) σ i ≡ σ-iterate a σ (σ-iterate b σ i)

σ-iterate-add :
  ∀ {n} (σ : Fin n → Fin n) (a b : ℕ) (i : Fin n) →
  σ-iterate (a ℕ+ b) σ i ≡ σ-iterate a σ (σ-iterate b σ i)
σ-iterate-add σ zero    b i = refl
σ-iterate-add σ (suc a) b i = cong σ (σ-iterate-add σ a b i)

------------------------------------------------------------------------
-- HasOrderPerm-multiple — order at any positive multiple.

HasOrderPerm-multiple :
  ∀ {n} (σ : Fin n → Fin n) (k m : ℕ) →
  HasOrderPerm σ k → HasOrderPerm σ (m ℕ* k)
HasOrderPerm-multiple σ k zero    σ-ord i = refl
HasOrderPerm-multiple σ k (suc m) σ-ord i =
  trans (σ-iterate-add σ k (m ℕ* k) i)
  (trans (cong (σ-iterate k σ)
               (HasOrderPerm-multiple σ k m σ-ord i))
         (σ-ord i))
