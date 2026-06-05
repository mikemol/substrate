------------------------------------------------------------------------
-- Substrate.Algebra.Q.Sub
--
-- ℚ subtraction `_-ℚ_` (via addition + negation). One canonical operator per
-- file (carrier-locality policy; see scratch/carrier_locality_policy.md).
-- Re-exported by Substrate.Algebra.Q.Arithmetic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Sub where

open import Substrate.Algebra.Q using (ℚ)
open import Substrate.Algebra.Q.Add using (_+ℚ_)
open import Substrate.Algebra.Q.Neg using (-ℚ_)

_-ℚ_ : ℚ → ℚ → ℚ
p -ℚ q = p +ℚ (-ℚ q)
