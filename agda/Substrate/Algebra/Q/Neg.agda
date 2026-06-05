------------------------------------------------------------------------
-- Substrate.Algebra.Q.Neg
--
-- ℚ negation `-ℚ_`. One canonical operator per file (carrier-locality policy;
-- see scratch/carrier_locality_policy.md). Re-exported by
-- Substrate.Algebra.Q.Arithmetic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Neg where

open import Substrate.Algebra.Z using (-ℤ_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1)

-ℚ_ : ℚ → ℚ
-ℚ q = mkℚ (-ℤ (num q)) (den-1 q)
