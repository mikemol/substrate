------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.CFInvariance.MulMonoStrict
--
-- Defines: mul-mono-strict
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.GCD.CFInvariance; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.CFInvariance.MulMonoStrict where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.GCD.CFInvariance.Private


mul-mono-strict : (r b n : ℕ) → r < suc b → r * suc n < suc b * suc n
mul-mono-strict r b n (s≤s r≤b) =
  ≤-<-trans (*-monoˡ-≤ (suc n) r≤b) (s≤s (n≤m+n n (b * suc n)))
