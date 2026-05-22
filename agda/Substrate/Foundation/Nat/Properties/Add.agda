------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Add
--
-- Addition properties on ℕ: identity, suc-step, associativity,
-- commutativity. Substrate-native, built on Foundation.Nat + Eq.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Add where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

+-identityˡ : (n : ℕ) → zero + n ≡ n
+-identityˡ _ = refl

+-identityʳ : (n : ℕ) → n + zero ≡ n
+-identityʳ zero    = refl
+-identityʳ (suc n) = cong suc (+-identityʳ n)

+-suc : (m n : ℕ) → m + suc n ≡ suc (m + n)
+-suc zero    _ = refl
+-suc (suc m) n = cong suc (+-suc m n)

+-assoc : (m n k : ℕ) → (m + n) + k ≡ m + (n + k)
+-assoc zero    _ _ = refl
+-assoc (suc m) n k = cong suc (+-assoc m n k)

+-comm : (m n : ℕ) → m + n ≡ n + m
+-comm zero    n = sym (+-identityʳ n)
+-comm (suc m) n = trans (cong suc (+-comm m n)) (sym (+-suc n m))
