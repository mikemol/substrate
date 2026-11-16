------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.TakeCong
--
-- Defines: take-cong
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.TakeCong where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Category.UniversalProperty.ExtrudeIOCostream
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
private variable O : Set
open import Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Approx



------------------------------------------------------------------------
-- ③ SOUNDNESS for finite observation: bisimilar costreams have EQUAL finite prefixes (every take agrees).
------------------------------------------------------------------------
take-cong : (n : ℕ) {c d : CoIO O} → c ≈ᶜ d → take-coio n c ≡ take-coio n d
take-cong zero    p = refl
take-cong (suc n) p = cong₂ _∷_ (head≈ p) (take-cong n (rest≈ p))
