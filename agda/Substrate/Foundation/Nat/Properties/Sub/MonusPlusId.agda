------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Sub.MonusPlusId
--
-- Defines: ∸-+-id
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Sub; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Sub.MonusPlusId where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans
-- ∸-+-id : reconstruction-from-subtraction identity.
--
-- For k ≤ m, subtracting k from m and adding it back yields m.
-- Induction on k (the smaller side); m's structural form is forced
-- on the suc-suc case by k ≤ m.
------------------------------------------------------------------------

∸-+-id : (m k : ℕ) → k ≤ m → (m ∸ k) ℕ+ k ≡ m
∸-+-id m       zero    _         = +ℕ-identityʳ m
∸-+-id (suc m) (suc k) (s≤s k≤m) =
  trans (+ℕ-suc (m ∸ k) k) (cong suc (∸-+-id m k k≤m))
