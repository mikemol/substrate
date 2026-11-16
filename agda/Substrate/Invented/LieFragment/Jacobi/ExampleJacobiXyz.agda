------------------------------------------------------------------------
-- Substrate.Invented.LieFragment.Jacobi.ExampleJacobiXyz
--
-- Defines: example-jacobi-xyz
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Invented.LieFragment.Jacobi; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Invented.LieFragment.Jacobi.ExampleJacobiXyz where

open import Substrate.Invented.LieFragment
open import Substrate.Invented.LieFragment.Jacobi.LieAlgExpr
open import Substrate.Invented.LieFragment.Jacobi.ApproxL



------------------------------------------------------------------------
-- 4. Worked example at concrete generators.
--
-- Jacobi applied to the three basis generators (gen x, gen y, gen z)
-- — the canonical Lie-axiom verification.
------------------------------------------------------------------------

example-jacobi-xyz :
  ((bracket (gen x) (bracket (gen y) (gen z)) ⊕L
    bracket (gen y) (bracket (gen z) (gen x))) ⊕L
   bracket (gen z) (bracket (gen x) (gen y)))
  ≈L zero-L
example-jacobi-xyz = jacobi-L (gen x) (gen y) (gen z)
