------------------------------------------------------------------------
-- Substrate.Algebra.Nat.DivMod.Unique.NoWrap
--
-- Defines: no-wrap
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.DivMod.Unique; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.DivMod.Unique.NoWrap where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.DivMod.Unique.Private


no-wrap : (b Y r : ℕ) → r ≡ suc b ℕ+ Y → r < suc b → ⊥
no-wrap b Y r eq lt =
  <-irrefl (suc b ℕ+ Y)
    (≤-trans (subst (λ z → suc z ≤ suc b) eq lt) (m≤m+n (suc b) Y))
