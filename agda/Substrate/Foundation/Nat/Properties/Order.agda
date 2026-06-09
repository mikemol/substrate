------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order
--
-- Order properties on ℕ: reflexivity, suc-step, irreflexivity.
-- Building blocks for the Mod / Cyclic arc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order where

open import Substrate.Foundation.Nat
  using (ℕ; zero; suc; _+_; _*_; _≤_; _<_; s≤s; z≤n)
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

------------------------------------------------------------------------
-- <→≤ : strict-to-loose order inclusion.
--
-- `m < n` is `suc m ≤ n`, so `n = suc n'` with `m ≤ n'`. Lift via
-- ≤-suc-r to `m ≤ suc n' = n`.
------------------------------------------------------------------------

<→≤ : ∀ {m n} → m < n → m ≤ n
<→≤ (s≤s p) = ≤-suc-r p

------------------------------------------------------------------------
-- ≤-trans / ≤-<-trans : transitivity of ≤ (and the mixed variant).
------------------------------------------------------------------------

≤-trans : ∀ {m n p} → m ≤ n → n ≤ p → m ≤ p
≤-trans z≤n        _         = z≤n
≤-trans (s≤s m≤n)  (s≤s n≤p) = s≤s (≤-trans m≤n n≤p)

≤-<-trans : ∀ {m n p} → m ≤ n → n < p → m < p
≤-<-trans m≤n n<p = ≤-trans (s≤s m≤n) n<p

------------------------------------------------------------------------
-- ≤-tight: if suc m ≤ suc b AND ¬ (suc m ≤ b), then m ≡ b.
--
-- Used by DivMod reconstruction: when the mod-suc wraps (the NO
-- branch of `suc (a mod-suc b) <? suc b`), the remainder is exactly b.
------------------------------------------------------------------------

open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

≤-tight : (m b : ℕ) → suc m ≤ suc b → ¬ (suc m ≤ b) → m ≡ b
≤-tight zero    zero    _         _      = refl
≤-tight zero    (suc b) _         ¬sm≤b  = ⊥-elim (¬sm≤b (s≤s z≤n))
≤-tight (suc m) zero    (s≤s ()) _
≤-tight (suc m) (suc b) (s≤s sm≤sb) ¬sm≤b' =
  cong suc (≤-tight m b sm≤sb (λ p → ¬sm≤b' (s≤s p)))

------------------------------------------------------------------------
-- Additive order: a summand is ≤ the sum. (The chirality pair.)
------------------------------------------------------------------------

m≤m+n : (m n : ℕ) → m ≤ m + n
m≤m+n zero    n = z≤n
m≤m+n (suc m) n = s≤s (m≤m+n m n)

n≤m+n : (m n : ℕ) → n ≤ m + n
n≤m+n zero    n = ≤-refl n
n≤m+n (suc m) n = ≤-suc-r (n≤m+n m n)

------------------------------------------------------------------------
-- Monotonicity: right-summand and left-factor preserve ≤.
------------------------------------------------------------------------

+-monoʳ-≤ : (k : ℕ) {m n : ℕ} → m ≤ n → k + m ≤ k + n
+-monoʳ-≤ zero    p = p
+-monoʳ-≤ (suc k) p = s≤s (+-monoʳ-≤ k p)

+-monoˡ-≤ : (k : ℕ) {m n : ℕ} → m ≤ n → m + k ≤ n + k
+-monoˡ-≤ k z≤n     = n≤m+n _ k
+-monoˡ-≤ k (s≤s p) = s≤s (+-monoˡ-≤ k p)

+-mono-≤ : {m n p q : ℕ} → m ≤ n → p ≤ q → m + p ≤ n + q
+-mono-≤ {n = n} {p = p} mn pq = ≤-trans (+-monoˡ-≤ p mn) (+-monoʳ-≤ n pq)

*-monoˡ-≤ : (n : ℕ) {r b : ℕ} → r ≤ b → r * n ≤ b * n
*-monoˡ-≤ n z≤n      = z≤n
*-monoˡ-≤ n (s≤s p)  = +-monoʳ-≤ n (*-monoˡ-≤ n p)

*-monoʳ-≤ : (n : ℕ) {r b : ℕ} → r ≤ b → n * r ≤ n * b
*-monoʳ-≤ zero    p = z≤n
*-monoʳ-≤ (suc n) p = +-mono-≤ p (*-monoʳ-≤ n p)
