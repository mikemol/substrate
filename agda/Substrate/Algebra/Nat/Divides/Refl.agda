------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Divides.Refl
--
-- ∣-refl : m ∣ m. Witness: divides 1 (sym (*-identityˡ m)).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Divides.Refl where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Mul using (*-identityˡ)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym

∣-refl : ∀ {m} → m ∣ m
∣-refl {m} = divides 1 (sym (*-identityˡ m))
