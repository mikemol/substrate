------------------------------------------------------------------------
-- Witness: the round trip computes — encoding 5 and reading it back
-- returns 5.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.ToBinFiveValue where

open import Substrate.Algebra.Wedge.Bin.Value
open import Substrate.Algebra.Wedge.BinBridge.ToBin
open import Substrate.Foundation.Eq

toBin-five-value : value (toBin 3 5) ≡ 5
toBin-five-value = refl
