------------------------------------------------------------------------
-- Substrate.Foundation.Nat.NonZero
--
-- Defines: NonZero, nz-suc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.NonZero where

open import Substrate.Foundation.Nat.Nat



------------------------------------------------------------------------
-- NonZero predicate (used by GCD / quotient arcs).
------------------------------------------------------------------------

data NonZero : ℕ → Set where
  nz-suc : ∀ {n} → NonZero (suc n)

instance
  nz : ∀ {n} → NonZero (suc n)
  nz = nz-suc
