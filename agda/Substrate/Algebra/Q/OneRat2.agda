------------------------------------------------------------------------
-- Substrate.Algebra.Q.OneRat2
--
-- Defines: -1ℚ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.OneRat2 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.OneInt2
open import Substrate.Algebra.Z.OneInt2
open import Substrate.Algebra.Q.Rat



-1ℚ : ℚ
-1ℚ = mkℚ -1ℤ 0  -- -1/1
