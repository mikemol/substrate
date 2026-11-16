------------------------------------------------------------------------
-- The weight of a carry-out: 2ⁿ, defined by DOUBLING rather than as 2 ^ n
-- so that `pow2 (suc n) = pow2 n ℕ+ pow2 n` holds definitionally — matching
-- morton's own doubling shape, so no `*` is needed in the adder proof.
-- Context: Substrate/Algebra/Wedge/BinArith/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinArith.Pow2 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus

pow2 : ℕ → ℕ
pow2 zero    = suc zero
pow2 (suc n) = pow2 n ℕ+ pow2 n
