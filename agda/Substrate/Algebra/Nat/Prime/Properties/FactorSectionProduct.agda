------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.FactorSectionProduct
--
-- Defines: factor-section-product
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.FactorSectionProduct where

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
open import Substrate.Algebra.Nat.Prime.Properties.FactorSection



-- the section's product is the original positive: product (factorize (suc m)) ≡ suc m.
-- (The existence round-trip, exposed directly for the ℚ₊ lift.)
factor-section-product : (m : ℕ) → product (factor-section m) ≡ suc m
factor-section-product m = proj₂ (proj₂ (factorize! (suc m) (s≤s z≤n)))
