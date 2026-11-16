------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Divides.Zero
--
-- ∣-zero : m ∣ 0. Trivially, 0 = 0 * m.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Divides.Zero where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)
open import Substrate.Foundation.Eq

∣-zero : ∀ m → m ∣ 0
∣-zero m = divides 0 refl
