------------------------------------------------------------------------
-- The full adder's carry bit (the majority function).
-- Context: Substrate/Algebra/Wedge/BinArith/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinArith.CarryBit where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.Or
open import Substrate.Foundation.Bool.Xor

carryBit : Bool → Bool → Bool → Bool
carryBit c a b = (a ∧ b) ∨ (c ∧ (a xor b))
