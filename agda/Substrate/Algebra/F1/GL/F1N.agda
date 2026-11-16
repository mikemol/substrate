------------------------------------------------------------------------
-- Substrate.Algebra.F1.GL.F1N
--
-- Defines: F₁ⁿ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F1.GL; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F1.GL.F1N where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.PointedSet



------------------------------------------------------------------------
-- 1. The F₁-vector space of dimension n: (Fin (suc n), zero).
------------------------------------------------------------------------

-- ⟡set1-paydown: PointedSet is now carrier-indexed; the carrier is Fin (suc n).
F₁ⁿ : (n : ℕ) → PointedSet (Fin (suc n))
F₁ⁿ n = record
  { base = zero
  }
