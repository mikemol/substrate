------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.ApproxTrans
--
-- Defines: ≈ᶜ-trans
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.ApproxTrans where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.UniversalProperty.ExtrudeIOCostream
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
private variable O : Set
open import Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Approx



≈ᶜ-trans : {c d e : CoIO O} → c ≈ᶜ d → d ≈ᶜ e → c ≈ᶜ e
head≈ (≈ᶜ-trans p q) = trans (head≈ p) (head≈ q)
rest≈ (≈ᶜ-trans p q) = ≈ᶜ-trans (rest≈ p) (rest≈ q)
