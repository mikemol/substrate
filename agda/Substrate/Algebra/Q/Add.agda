------------------------------------------------------------------------
-- Substrate.Algebra.Q.Add
--
-- ℚ addition `_+ℚ_`:  a/b + c/d = (a*d + c*b) / (b*d), over the CANONICAL ℤ
-- ops (Substrate.Algebra.Z.Arithmetic — imported, not forked). One canonical
-- operator per file (carrier-locality policy; see
-- scratch/carrier_locality_policy.md). Re-exported by
-- Substrate.Algebra.Q.Arithmetic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Add where
open import Substrate.Algebra.Z.Add
open import Substrate.Algebra.Z.Mul

open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.Z.Int

open import Substrate.Algebra.Q.Rat

_+ℚ_ : ℚ → ℚ → ℚ
p +ℚ q =
  let a  = num p
      b₋ = den-1 p
      c  = num q
      d₋ = den-1 q
      b  = suc b₋
      d  = suc d₋
      n  = (a *ℤ (+ d)) +ℤ (c *ℤ (+ b))
      -- new denominator: b * d = suc b₋ * suc d₋
      d' = b * d
  in mkℚ n (d' ∸ 1)
