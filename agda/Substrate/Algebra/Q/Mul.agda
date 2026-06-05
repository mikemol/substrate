------------------------------------------------------------------------
-- Substrate.Algebra.Q.Mul
--
-- ℚ multiplication `_*ℚ_`:  (a/b) * (c/d) = (a*c) / (b*d), over the CANONICAL
-- ℤ ops (imported, not forked). One canonical operator per file
-- (carrier-locality policy; see scratch/carrier_locality_policy.md).
-- Re-exported by Substrate.Algebra.Q.Arithmetic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Mul where

open import Substrate.Foundation.Nat using (suc; _*_; _∸_)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1)

_*ℚ_ : ℚ → ℚ → ℚ
p *ℚ q =
  let a  = num p
      b₋ = den-1 p
      c  = num q
      d₋ = den-1 q
      b  = suc b₋
      d  = suc d₋
      n  = a *ℤ c
      d' = b * d
  in mkℚ n (d' ∸ 1)
