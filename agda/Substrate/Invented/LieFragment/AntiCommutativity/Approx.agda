------------------------------------------------------------------------
-- Substrate.Invented.LieFragment.AntiCommutativity.Approx
--
-- Defines: _≈ₐ_, bracket-cong, refl-≈, swap, sym-≈, trans-≈
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Invented.LieFragment.AntiCommutativity; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Invented.LieFragment.AntiCommutativity.Approx where

open import Substrate.Invented.LieFragment



------------------------------------------------------------------------
-- 1. The Setoid relation _≈ₐ_.
--
-- An equational quotient on LieExpr capturing the F₂-flavoured
-- anti-commutativity axiom. Standard Setoid constructors
-- (reflexivity, symmetry, transitivity) plus the headline `swap`
-- axiom and bracket-congruence.
------------------------------------------------------------------------

data _≈ₐ_ : LieExpr → LieExpr → Set where
  refl-≈ :
    {e : LieExpr} → e ≈ₐ e
  sym-≈ :
    {e₁ e₂ : LieExpr} → e₁ ≈ₐ e₂ → e₂ ≈ₐ e₁
  trans-≈ :
    {e₁ e₂ e₃ : LieExpr} → e₁ ≈ₐ e₂ → e₂ ≈ₐ e₃ → e₁ ≈ₐ e₃
  swap :
    (x y : LieExpr) → bracket x y ≈ₐ bracket y x
  bracket-cong :
    {x₁ x₂ y₁ y₂ : LieExpr} →
    x₁ ≈ₐ x₂ → y₁ ≈ₐ y₂ → bracket x₁ y₁ ≈ₐ bracket x₂ y₂
