------------------------------------------------------------------------
-- Substrate.Algebra.Z.Sub
--
-- ℤ subtraction `_-ℤ_` (via addition + negation). One canonical operator per
-- file (carrier-locality policy; see scratch/carrier_locality_policy.md).
--
-- Definitions only (laws live in Z.Properties). Re-exported by
-- Substrate.Algebra.Z.Arithmetic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Sub where

open import Substrate.Algebra.Z using (ℤ; -ℤ_)
open import Substrate.Algebra.Z.Add using (_+ℤ_)

infixl 6 _-ℤ_

-- integer subtraction.
_-ℤ_ : ℤ → ℤ → ℤ
a -ℤ b = a +ℤ (-ℤ b)
