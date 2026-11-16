------------------------------------------------------------------------
-- Substrate.Algebra.Q.Equiv.ApproxRat
--
-- Defines: _≈ℚ_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Equiv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Equiv.ApproxRat where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Mul
open import Substrate.Algebra.Q.Rat
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 1. Cross-multiplication equality. (den = suc (den-1), written literally so
--    the cancel-by-positive lemma's `+ suc d` form matches definitionally.)
------------------------------------------------------------------------

_≈ℚ_ : ℚ → ℚ → Set
p ≈ℚ q = (num p *ℤ (+ suc (den-1 q))) ≡ (num q *ℤ (+ suc (den-1 p)))
