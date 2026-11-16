------------------------------------------------------------------------
-- THE RESIDUE, COMPUTED: predicted 5, actual 4. The prediction is sound
-- (4 ≤ 5, by the `fits` field Trimmed carries) and it is not tight — and
-- the carrier holds both readings instead of collapsing to either.
-- Context: Substrate/Algebra/Wedge/BinMul/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinMul.MulThreeFiveResidue where

open import Substrate.Algebra.Wedge.BinTrim.Trim
open import Substrate.Algebra.Wedge.BinTrim.ExactWidth
open import Substrate.Algebra.Wedge.BinMul.ProductBits
open import Substrate.Foundation.Eq

mul-three-five-residue : exact-width (trim product-bits) ≡ 4
mul-three-five-residue = refl
