------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.ApproxRefl
--
-- Defines: ≈ᶜ-refl
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.ApproxRefl where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.UniversalProperty.ExtrudeIOCostream
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
private variable O : Set
open import Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Approx



------------------------------------------------------------------------
-- ② AN EQUIVALENCE (refl/sym/trans, coinductive):
------------------------------------------------------------------------
≈ᶜ-refl : (c : CoIO O) → c ≈ᶜ c
head≈ (≈ᶜ-refl c) = refl
rest≈ (≈ᶜ-refl c) = ≈ᶜ-refl (emit-rest c)
