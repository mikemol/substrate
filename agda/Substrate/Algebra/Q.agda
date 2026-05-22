------------------------------------------------------------------------
-- Substrate.Algebra.Q
--
-- Q2 of the constructive ℚ arc per [scratch/q_arc_plan.md].
--
-- Substrate-native ℚ as a record bundling:
--   * num  : ℤ        (the numerator)
--   * den-1 : ℕ       (denominator stored as denom-minus-1, so the
--                      actual denominator is `suc den-1`, never 0)
--
-- This encoding guarantees non-zero denominator at the type level
-- (no proof obligation needed). The trade-off: the actual
-- denominator value is `suc den-1`, requiring a small accessor
-- (`denominator`) for use sites. Canonical-form reduction (gcd
-- normalisation) lands at Q4.
--
-- Per [[feedback-categorical-name-first]]: "ℚ as integer-pair
-- quotient" is the standard constructive presentation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 0ℤ; 1ℤ; -1ℤ)

------------------------------------------------------------------------
-- 1. The ℚ record.
------------------------------------------------------------------------

record ℚ : Set where
  constructor mkℚ
  field
    num   : ℤ
    den-1 : ℕ

open ℚ public

------------------------------------------------------------------------
-- 2. Accessors.
------------------------------------------------------------------------

denominator : ℚ → ℕ
denominator q = suc (den-1 q)

numerator : ℚ → ℤ
numerator = num

------------------------------------------------------------------------
-- 3. Named constants.
------------------------------------------------------------------------

0ℚ : ℚ
0ℚ = mkℚ 0ℤ 0   -- 0/1

1ℚ : ℚ
1ℚ = mkℚ 1ℤ 0   -- 1/1

-1ℚ : ℚ
-1ℚ = mkℚ -1ℤ 0  -- -1/1

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
