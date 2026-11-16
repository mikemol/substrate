------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Cancel.PlusCancelL
--
-- Defines: +-cancelˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Cancel; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Cancel.PlusCancelL where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.SucInjective
open import Substrate.Foundation.Eq
+-cancelˡ : (k : ℕ) {m n : ℕ} → (k ℕ+ m) ≡ (k ℕ+ n) → m ≡ n
+-cancelˡ zero    eq = eq
+-cancelˡ (suc k) eq = +-cancelˡ k (suc-injective eq)
