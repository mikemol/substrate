------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.GcdPos.GcdSucPos
--
-- Defines: gcd-suc-pos
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.GCD.GcdPos; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.GcdPos.GcdSucPos where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.GCD.GcdN
open import Substrate.Algebra.Nat.GCD.GcdDividesRight
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.GCD.GcdPos.GcdPos



-- The order form (positivity), for callers that want `0 < gcd` directly.
gcd-suc-pos : (n d : ℕ) → 0 < gcd-ℕ n (suc d)
gcd-suc-pos n d = subst (0 <_) (sym (proj₂ (gcd-pos n d))) (s≤s z≤n)
