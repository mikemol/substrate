------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.GcdPos.Zerosuc
--
-- Defines: zero∤suc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.GCD.GcdPos; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.GcdPos.Zerosuc where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Subst



zero∤suc : {m : ℕ} → zero ∣ suc m → ⊥
zero∤suc (divides q eq) with trans eq (*-zeroʳ q)
... | ()
