------------------------------------------------------------------------
-- Substrate.Invented.LieFragment.AntiCommutativity
--
-- D3 of the Closure-debt arc per [scratch/closure_arc_plan.md].
--
-- Surfaces the first Lie-algebra axiom for the LieFragment:
-- ANTI-COMMUTATIVITY [x, y] = -[y, x]. In the substrate's F₂
-- context (characteristic 2: -x = x), anti-commutativity reduces
-- to COMMUTATIVITY [x, y] = [y, x]. The Setoid relation `_≈ₐ_`
-- below captures this equational quotient on LieExpr.
--
-- Per [[feedback-comments-dont-overclaim]]: this is F₂-flavoured
-- anti-commutativity (= commutativity at characteristic 2). Over
-- a field of characteristic ≠ 2 the Lie axiom is strictly stronger
-- (requires a negation), but the substrate's F₂-centric framing
-- makes the simpler form correct here.
--
-- D4 (the next slice) adds the Jacobi identity; D3 + D4 jointly
-- give the full Lie-algebra equational quotient at the LieFragment
-- level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Invented.LieFragment.AntiCommutativity where

open import Substrate.Invented.LieFragment using (LieExpr; gen; bracket)

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

------------------------------------------------------------------------
-- 2. The headline axiom (named).
--
-- [x, y] ≈ₐ [y, x] — the F₂-anti-commutativity Lie axiom.
------------------------------------------------------------------------

anti-commutative :
  (x y : LieExpr) → bracket x y ≈ₐ bracket y x
anti-commutative = swap

------------------------------------------------------------------------
-- 3. Consequence: swapping twice returns to the original.
--
-- [x, y] ≈ₐ [y, x] ≈ₐ [x, y]. Standard double-swap-is-identity.
------------------------------------------------------------------------

double-swap :
  (x y : LieExpr) → bracket x y ≈ₐ bracket x y
double-swap x y = trans-≈ (swap x y) (swap y x)

------------------------------------------------------------------------
-- 4. Worked-example: [x, y] ≈ₐ [y, x] at concrete generators.
------------------------------------------------------------------------

open import Substrate.Invented.LieFragment using (x; y; z)

example-xy-≈-yx :
  bracket (gen x) (gen y) ≈ₐ bracket (gen y) (gen x)
example-xy-≈-yx = swap (gen x) (gen y)

------------------------------------------------------------------------
-- 5. Capstone.
--
-- The Setoid relation _≈ₐ_ provides the equational structure that
-- a Lie-algebra quotient over LieExpr would identify; for the
-- substrate's F₂ framing, this is enough. D4 extends with Jacobi
-- to complete the Lie axioms; together they define
-- Substrate.Invented.LieFragment.LieEq for the full quotient.
------------------------------------------------------------------------
