------------------------------------------------------------------------
-- Substrate.Algebra.Q.Equiv.ApproxRatSym
--
-- Defines: ≈ℚ-sym
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Equiv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Equiv.ApproxRatSym where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Mul
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Equiv.ApproxRat
open import Substrate.Foundation.Eq.Sym



≈ℚ-sym : {a b : ℚ} → a ≈ℚ b → b ≈ℚ a
≈ℚ-sym e = sym e
