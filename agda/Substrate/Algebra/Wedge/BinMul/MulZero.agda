------------------------------------------------------------------------
-- Witness: multiplying by zero stays at the predicted width and is zero.
-- Context: Substrate/Algebra/Wedge/BinMul/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinMul.MulZero where

open import Substrate.Algebra.Wedge.Bin.Value
open import Substrate.Algebra.Wedge.BinMul.MulU
open import Substrate.Algebra.Wedge.BinMul.Zeros
open import Substrate.Algebra.Wedge.BinMul.Three
open import Substrate.Foundation.Eq

mul-zero : value (mulU three (zeros 3)) ≡ 0
mul-zero = refl
