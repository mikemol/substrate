------------------------------------------------------------------------
-- Substrate.Algebra.Q.Neg
--
-- ℚ negation `-ℚ_`. One canonical operator per file (carrier-locality policy;
-- see scratch/carrier_locality_policy.md). Re-exported by
-- Substrate.Algebra.Q.Arithmetic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Neg where

open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Q.Rat

-ℚ_ : ℚ → ℚ
-ℚ q = mkℚ (-ℤ (num q)) (den-1 q)
