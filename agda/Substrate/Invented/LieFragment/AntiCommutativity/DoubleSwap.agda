------------------------------------------------------------------------
-- Substrate.Invented.LieFragment.AntiCommutativity.DoubleSwap
--
-- Defines: double-swap
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Invented.LieFragment.AntiCommutativity; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Invented.LieFragment.AntiCommutativity.DoubleSwap where

open import Substrate.Invented.LieFragment
open import Substrate.Invented.LieFragment.AntiCommutativity.Approx



------------------------------------------------------------------------
-- 3. Consequence: swapping twice returns to the original.
--
-- [x, y] ≈ₐ [y, x] ≈ₐ [x, y]. Standard double-swap-is-identity.
------------------------------------------------------------------------

double-swap :
  (x y : LieExpr) → bracket x y ≈ₐ bracket x y
double-swap x y = trans-≈ (swap x y) (swap y x)
