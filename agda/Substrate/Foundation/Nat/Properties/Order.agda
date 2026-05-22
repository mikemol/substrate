------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order
--
-- Order properties on ℕ: reflexivity, suc-step, irreflexivity.
-- Building blocks for the Mod / Cyclic arc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order where

open import Substrate.Foundation.Nat
  using (ℕ; zero; suc; _≤_; _<_; s≤s; z≤n)
open import Substrate.Foundation.Empty using (⊥)

≤-suc-r : ∀ {m n} → m ≤ n → m ≤ suc n
≤-suc-r z≤n       = z≤n
≤-suc-r (s≤s p)   = s≤s (≤-suc-r p)

<-suc-r : ∀ {m n} → m < n → m < suc n
<-suc-r = ≤-suc-r

≤-refl : (n : ℕ) → n ≤ n
≤-refl zero    = z≤n
≤-refl (suc n) = s≤s (≤-refl n)

<-suc-self : (n : ℕ) → n < suc n
<-suc-self n = ≤-refl (suc n)

<-irrefl : (n : ℕ) → suc n ≤ n → ⊥
<-irrefl (suc n) (s≤s p) = <-irrefl n p
