------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.ApproxSym
--
-- Defines: ≈ᶜ-sym
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.ApproxSym where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.UniversalProperty.ExtrudeIOCostream
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
private variable O : Set
open import Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Approx



≈ᶜ-sym : {c d : CoIO O} → c ≈ᶜ d → d ≈ᶜ c
head≈ (≈ᶜ-sym p) = sym (head≈ p)
rest≈ (≈ᶜ-sym p) = ≈ᶜ-sym (rest≈ p)
