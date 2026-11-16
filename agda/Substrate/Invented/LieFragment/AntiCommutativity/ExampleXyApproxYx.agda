------------------------------------------------------------------------
-- Substrate.Invented.LieFragment.AntiCommutativity.ExampleXyApproxYx
--
-- Defines: example-xy-≈-yx
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Invented.LieFragment.AntiCommutativity; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Invented.LieFragment.AntiCommutativity.ExampleXyApproxYx where

open import Substrate.Invented.LieFragment
open import Substrate.Invented.LieFragment.AntiCommutativity.Approx



------------------------------------------------------------------------
-- 4. Worked-example: [x, y] ≈ₐ [y, x] at concrete generators.
------------------------------------------------------------------------


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
