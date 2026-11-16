------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Approx
--
-- Defines: _≈ᶜ_, head≈, rest≈
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Approx where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.UniversalProperty.ExtrudeIOCostream
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
private variable O : Set

infix 4 _≈ᶜ_


------------------------------------------------------------------------
-- ① BISIMILARITY on the unbounded emit: same head, bisimilar rest (coinductive — the observational equality).
------------------------------------------------------------------------
record _≈ᶜ_ {O : Set} (c d : CoIO O) : Set where
  coinductive
  field
    head≈ : emit-head c ≡ emit-head d
    rest≈ : emit-rest c ≈ᶜ emit-rest d
open _≈ᶜ_ public
