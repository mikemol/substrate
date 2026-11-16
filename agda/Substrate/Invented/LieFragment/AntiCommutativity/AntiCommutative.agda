------------------------------------------------------------------------
-- Substrate.Invented.LieFragment.AntiCommutativity.AntiCommutative
--
-- Defines: anti-commutative
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Invented.LieFragment.AntiCommutativity; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Invented.LieFragment.AntiCommutativity.AntiCommutative where

open import Substrate.Invented.LieFragment
open import Substrate.Invented.LieFragment.AntiCommutativity.Approx



------------------------------------------------------------------------
-- 2. The headline axiom (named).
--
-- [x, y] ≈ₐ [y, x] — the F₂-anti-commutativity Lie axiom.
------------------------------------------------------------------------

anti-commutative :
  (x y : LieExpr) → bracket x y ≈ₐ bracket y x
anti-commutative = swap
