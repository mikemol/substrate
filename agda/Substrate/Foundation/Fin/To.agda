------------------------------------------------------------------------
-- Substrate.Foundation.Fin.To
--
-- Defines: toℕ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.To where

open import Substrate.Foundation.Nat
  renaming (_<_ to _<ℕ_; _≤_ to _≤ℕ_)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Empty
open import Substrate.Foundation.Negation
open import Substrate.Foundation.Fin.Fin


------------------------------------------------------------------------
-- toℕ / fromℕ.
------------------------------------------------------------------------

toℕ : {n : ℕ} → Fin n → ℕ
toℕ zero    = zero
toℕ (suc i) = suc (toℕ i)
