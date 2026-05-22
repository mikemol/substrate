------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Divides.Mul
--
-- Multiplicative divisibility:
--   m∣m*n : m ∣ m * n   (right factor)
--   n∣m*n : n ∣ m * n   (left factor)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Divides.Mul where

open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-comm)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)

m∣m*n : ∀ {m} n → m ∣ m * n
m∣m*n {m} n = divides n (*-comm m n)

n∣m*n : ∀ m {n} → n ∣ m * n
n∣m*n m {n} = divides m refl
