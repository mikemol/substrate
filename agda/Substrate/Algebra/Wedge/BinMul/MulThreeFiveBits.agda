------------------------------------------------------------------------
-- Witness: the product's bits are 15 read LSB-first.
-- Context: Substrate/Algebra/Wedge/BinMul/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinMul.MulThreeFiveBits where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.BinMul.ProductBits
open import Substrate.Foundation.Eq

mul-three-five-bits : product-bits ≡ true ∷ true ∷ true ∷ true ∷ false ∷ []
mul-three-five-bits = refl
