------------------------------------------------------------------------
-- The full adder, one bit: c ℕ+ a ℕ+ b = sum ℕ+ 2·carry. Eight Bool cases,
-- each `refl` — this is the whole arithmetic content of the ripple adder.
-- Context: Substrate/Algebra/Wedge/BinArith/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinArith.FullAdder where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Bool.Or
open import Substrate.Foundation.Bool.Xor
open import Substrate.Algebra.Wedge.BinArith.SumBit
open import Substrate.Algebra.Wedge.BinArith.CarryBit
open import Substrate.Foundation.Eq

full-adder : (c a b : Bool) →
  boolToℕ c ℕ+ (boolToℕ a ℕ+ boolToℕ b)
  ≡ boolToℕ (sumBit c a b) ℕ+ (boolToℕ (carryBit c a b) ℕ+ boolToℕ (carryBit c a b))
full-adder false false false = refl
full-adder false false true  = refl
full-adder false true  false = refl
full-adder false true  true  = refl
full-adder true  false false = refl
full-adder true  false true  = refl
full-adder true  true  false = refl
full-adder true  true  true  = refl
