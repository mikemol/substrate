------------------------------------------------------------------------
-- The product 3 × 5, landing at the PREDICTED width 2 + 3 = 5.
-- Context: Substrate/Algebra/Wedge/BinMul/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinMul.ProductBits where

open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.BinMul.MulU
open import Substrate.Algebra.Wedge.BinMul.Three
open import Substrate.Algebra.Wedge.BinMul.Five

product-bits : Bin 5
product-bits = mulU three five
