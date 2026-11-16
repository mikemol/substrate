------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.CFInvariance.PosTimesPos
--
-- Defines: pos-*-pos
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.GCD.CFInvariance; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.CFInvariance.PosTimesPos where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.GCD.CFInvariance.Private


pos-*-pos : (m n : ℕ) → 0 < m → 0 < m * suc n
pos-*-pos zero    n ()
pos-*-pos (suc m) n _ = s≤s z≤n

-- Multiplying a strict bound by a positive preserves it.
