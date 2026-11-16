------------------------------------------------------------------------
-- Substrate.Algebra.Z.Int
--
-- Defines: ℤ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Int where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus



------------------------------------------------------------------------
-- 1. The ℤ data type.
--
-- Two constructors:
--   * `+ n` for n ≥ 0 (so ℕ+ 0 is the unique zero, ℕ+ 1 = 1, etc.)
--   * `-suc n` for the negative integer -(suc n) (so -suc 0 = -1,
--     -suc 1 = -2, etc.)
------------------------------------------------------------------------

data ℤ : Set where
  +_    : ℕ → ℤ
  -suc_ : ℕ → ℤ
