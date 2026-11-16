------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Monus
--
-- Defines: _∸_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Monus where

open import Substrate.Foundation.Nat.Nat

infixl 6 _∸_


_∸_ : ℕ → ℕ → ℕ
m     ∸ zero  = m
zero  ∸ suc _ = zero
suc m ∸ suc n = m ∸ n

------------------------------------------------------------------------
-- Order: _≤_ and _<_ as inductive predicates.
------------------------------------------------------------------------
