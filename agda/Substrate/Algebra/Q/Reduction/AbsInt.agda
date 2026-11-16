------------------------------------------------------------------------
-- Substrate.Algebra.Q.Reduction.AbsInt
--
-- Defines: abs-ℤ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Reduction; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Reduction.AbsInt where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.OneRat
open import Substrate.Algebra.Q.OneRat2
open import Substrate.Algebra.Q.ZeroRat
open import Substrate.Foundation.Eq


abs-ℤ : ℤ → ℕ
abs-ℤ (+ n)    = n
abs-ℤ (-suc n) = suc n
