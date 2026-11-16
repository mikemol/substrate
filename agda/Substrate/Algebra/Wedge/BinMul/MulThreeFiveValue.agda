------------------------------------------------------------------------
-- Witness: 3 × 5 = 15.
-- Context: Substrate/Algebra/Wedge/BinMul/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinMul.MulThreeFiveValue where

open import Substrate.Algebra.Wedge.Bin.Value
open import Substrate.Algebra.Wedge.BinMul.ProductBits
open import Substrate.Foundation.Eq

mul-three-five-value : value product-bits ≡ 15
mul-three-five-value = refl
