------------------------------------------------------------------------
-- Substrate.Algebra.Z.Mul
--
-- ℤ multiplication `_*ℤ_` (sign-magnitude on the two-constructor +_/-suc_
-- form). One canonical operator per file (carrier-locality policy; see
-- scratch/carrier_locality_policy.md).
--
-- Definitions only (laws live in Z.Properties). Re-exported by
-- Substrate.Algebra.Z.Arithmetic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Mul where

open import Substrate.Foundation.Nat using (suc; _*_)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_)

infixl 7 _*ℤ_

-- integer multiplication (sign-magnitude).
_*ℤ_ : ℤ → ℤ → ℤ
(+ m)    *ℤ (+ n)    = + (m * n)
(+ m)    *ℤ (-suc n) = -ℤ (+ (m * suc n))
(-suc m) *ℤ (+ n)    = -ℤ (+ (suc m * n))
(-suc m) *ℤ (-suc n) = + (suc m * suc n)
