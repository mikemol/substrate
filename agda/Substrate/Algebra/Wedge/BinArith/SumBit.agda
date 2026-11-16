------------------------------------------------------------------------
-- The full adder's sum bit.
-- Context: Substrate/Algebra/Wedge/BinArith/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinArith.SumBit where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Xor

sumBit : Bool → Bool → Bool → Bool
sumBit c a b = c xor (a xor b)
