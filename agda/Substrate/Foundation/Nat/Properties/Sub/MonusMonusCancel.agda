------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Sub.MonusMonusCancel
--
-- Defines: ∸-∸-cancel
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Sub; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Sub.MonusMonusCancel where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Sub.MonusLeSelf
open import Substrate.Foundation.Nat.Properties.Sub.MMonusmEq0
open import Substrate.Foundation.Nat.Properties.Sub.MonusSucL
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans



------------------------------------------------------------------------
-- ∸-∸-cancel : double-subtracting a bounded `k` from `m` recovers `k`.
------------------------------------------------------------------------

∸-∸-cancel : (m k : ℕ) → k ≤ m → m ∸ (m ∸ k) ≡ k
∸-∸-cancel m       zero    _         = m∸m≡0 m
∸-∸-cancel (suc m) (suc k) (s≤s k≤m) =
  trans (∸-suc-l m (m ∸ k) (∸-≤-self m k))
        (cong suc (∸-∸-cancel m k k≤m))
