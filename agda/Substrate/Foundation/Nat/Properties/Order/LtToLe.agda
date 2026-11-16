------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.LtToLe
--
-- Defines: <→≤
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.LtToLe where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Order.LeSucR



------------------------------------------------------------------------
-- <→≤ : strict-to-loose order inclusion.
--
-- `m < n` is `suc m ≤ n`, so `n = suc n'` with `m ≤ n'`. Lift via
-- ≤-suc-r to `m ≤ suc n' = n`.
------------------------------------------------------------------------

<→≤ : ∀ {m n} → m < n → m ≤ n
<→≤ (s≤s p) = ≤-suc-r p
