------------------------------------------------------------------------
-- Substrate.Algebra.Q.ZeroRat
--
-- Defines: 0ℚ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.ZeroRat where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.ZeroInt
open import Substrate.Algebra.Z.ZeroInt
open import Substrate.Algebra.Q.Rat



------------------------------------------------------------------------
-- 3. Named constants.
------------------------------------------------------------------------

0ℚ : ℚ
0ℚ = mkℚ 0ℤ 0   -- 0/1
