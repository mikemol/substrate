------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Sub
--
-- Truncated subtraction (∸) lemmas.
--
--   ∸-+-id : (m k : ℕ) → k ≤ m → (m ∸ k) + k ≡ m
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Sub where

open import Substrate.Foundation.Nat
  using (ℕ; zero; suc; _+_; _∸_; _≤_; s≤s; z≤n)
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ; +-suc)
open import Substrate.Foundation.Nat.Properties.Order using (≤-refl; ≤-suc-r)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

------------------------------------------------------------------------
-- ∸-+-id : reconstruction-from-subtraction identity.
--
-- For k ≤ m, subtracting k from m and adding it back yields m.
-- Induction on k (the smaller side); m's structural form is forced
-- on the suc-suc case by k ≤ m.
------------------------------------------------------------------------

∸-+-id : (m k : ℕ) → k ≤ m → (m ∸ k) + k ≡ m
∸-+-id m       zero    _         = +-identityʳ m
∸-+-id (suc m) (suc k) (s≤s k≤m) =
  trans (+-suc (m ∸ k) k) (cong suc (∸-+-id m k k≤m))

------------------------------------------------------------------------
-- ∸-≤-self : truncated subtraction can only reduce.
------------------------------------------------------------------------

∸-≤-self : (m k : ℕ) → m ∸ k ≤ m
∸-≤-self m       zero    = ≤-refl m
∸-≤-self zero    (suc _) = z≤n
∸-≤-self (suc m) (suc k) = ≤-suc-r (∸-≤-self m k)

------------------------------------------------------------------------
-- m∸m≡0 : truncated subtraction of self is zero.
------------------------------------------------------------------------

m∸m≡0 : (m : ℕ) → m ∸ m ≡ 0
m∸m≡0 zero    = refl
m∸m≡0 (suc m) = m∸m≡0 m

------------------------------------------------------------------------
-- ∸-suc-l : when subtracting k ≤ m from (suc m), the suc survives.
------------------------------------------------------------------------

∸-suc-l : (m k : ℕ) → k ≤ m → suc m ∸ k ≡ suc (m ∸ k)
∸-suc-l m       zero    _         = refl
∸-suc-l (suc m) (suc k) (s≤s k≤m) = ∸-suc-l m k k≤m

------------------------------------------------------------------------
-- ∸-∸-cancel : double-subtracting a bounded `k` from `m` recovers `k`.
------------------------------------------------------------------------

∸-∸-cancel : (m k : ℕ) → k ≤ m → m ∸ (m ∸ k) ≡ k
∸-∸-cancel m       zero    _         = m∸m≡0 m
∸-∸-cancel (suc m) (suc k) (s≤s k≤m) =
  trans (∸-suc-l m (m ∸ k) (∸-≤-self m k))
        (cong suc (∸-∸-cancel m k k≤m))
