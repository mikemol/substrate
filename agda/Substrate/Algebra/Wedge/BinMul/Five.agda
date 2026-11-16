------------------------------------------------------------------------
-- 5 = 101, LSB-first, at width 3.
-- Context: Substrate/Algebra/Wedge/BinMul/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinMul.Five where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Bin.Carrier

five : Bin 3
five = true ∷ false ∷ true ∷ []
