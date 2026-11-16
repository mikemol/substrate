------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Le
--
-- Defines: _≤_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Le where

open import Substrate.Foundation.Nat.Nat

infix 4 _≤_


data _≤_ : ℕ → ℕ → Set where      -- ⟦shape:7ac77a03 z≤n,s≤s⟧
  z≤n : {n : ℕ}              → zero  ≤ n
  s≤s : {m n : ℕ} → m ≤ n → suc m ≤ suc n
