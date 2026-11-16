------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.FactorRetract
--
-- Defines: factor-retract
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.FactorRetract where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Foundation.List
open import Substrate.Foundation.WellFounded
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.DivMod.Unique.Private
open import Substrate.Algebra.Nat.WellFounded.LtWellFounded
open import Substrate.Algebra.Nat.WellFounded.Private
open import Substrate.Algebra.Nat.Prime
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.Prime.Properties.Factorize
open import Substrate.Algebra.Nat.Prime.Properties.Factorize2
open import Substrate.Algebra.Nat.Prime.Properties.Pred
open import Substrate.Algebra.Nat.Prime.Properties.FactorValue
open import Substrate.Algebra.Nat.Prime.Properties.FactorSection



-- F ∘ s ≡ id: pred (product (factorize (suc m))) ≡ pred (suc m) ≡ m.
factor-retract : (m : ℕ) → factor-value (factor-section m) ≡ m
factor-retract m = cong pred (proj₂ (proj₂ (factorize! (suc m) (s≤s z≤n))))
