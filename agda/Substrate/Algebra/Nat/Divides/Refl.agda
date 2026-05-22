------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Divides.Refl
--
-- ∣-refl : m ∣ m. Witness: divides 1 (sym (*-identityˡ m)).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Divides.Refl where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Nat.Properties.Mul using (*-identityˡ)
open import Substrate.Foundation.Eq using (_≡_; sym)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)

∣-refl : ∀ {m} → m ∣ m
∣-refl {m} = divides 1 (sym (*-identityˡ m))
