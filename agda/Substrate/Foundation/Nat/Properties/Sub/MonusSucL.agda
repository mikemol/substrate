------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Sub.MonusSucL
--
-- Defines: ∸-suc-l
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Sub; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Sub.MonusSucL where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
-- ∸-suc-l : when subtracting k ≤ m from (suc m), the suc survives.
------------------------------------------------------------------------

∸-suc-l : (m k : ℕ) → k ≤ m → suc m ∸ k ≡ suc (m ∸ k)
∸-suc-l m       zero    _         = refl
∸-suc-l (suc m) (suc k) (s≤s k≤m) = ∸-suc-l m k k≤m
