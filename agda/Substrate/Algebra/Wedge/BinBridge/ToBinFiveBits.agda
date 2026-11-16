------------------------------------------------------------------------
-- Witness: 5 at a 3-bit predicted width is 101, LSB-first.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.ToBinFiveBits where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.BinBridge.ToBin
open import Substrate.Foundation.Eq

toBin-five-bits : toBin 3 5 ≡ true ∷ false ∷ true ∷ []
toBin-five-bits = refl
