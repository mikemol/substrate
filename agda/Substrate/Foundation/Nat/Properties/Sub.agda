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
