------------------------------------------------------------------------
-- 3 = 11, LSB-first, at width 2.
-- Context: Substrate/Algebra/Wedge/BinMul/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinMul.Three where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Bin.Carrier

three : Bin 2
three = true ∷ true ∷ []
