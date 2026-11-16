------------------------------------------------------------------------
-- Substrate.Algebra.Q.RatOf
--
-- Defines: ℚ-of
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.RatOf where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Denominator



------------------------------------------------------------------------
-- 4. Smart constructor for integer-denominator ℚ.
--
-- Given (n : ℤ, d : ℕ, d-pos : "d is suc-something"), build mkℚ.
-- Convenient for downstream constructions.
------------------------------------------------------------------------

ℚ-of :
  (n : ℤ) (d : ℕ) → ℚ
ℚ-of n zero    = mkℚ n 0       -- treat 0-denominator input as 1
ℚ-of n (suc m) = mkℚ n m

------------------------------------------------------------------------
-- 5. Capstone for Q2.
--
-- ℚ carrier defined; non-zero denominator built into the encoding.
-- Q3 adds decidable equality; Q4 the gcd reduction.
------------------------------------------------------------------------
