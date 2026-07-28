------------------------------------------------------------------------
-- Substrate.Foundation.Fin.From
--
-- Defines: fromℕ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.From where

open import Substrate.Foundation.Nat
  renaming (_<_ to _<ℕ_; _≤_ to _≤ℕ_)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Empty
open import Substrate.Foundation.Negation
open import Substrate.Foundation.Fin.Fin


fromℕ : (n : ℕ) → Fin (suc n)
fromℕ zero    = zero
fromℕ (suc n) = suc (fromℕ n)
