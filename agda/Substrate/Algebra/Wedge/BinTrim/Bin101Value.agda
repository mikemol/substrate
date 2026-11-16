------------------------------------------------------------------------
-- Convention check: 101 read LSB-first is 5.
-- Context: Substrate/Algebra/Wedge/BinTrim/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinTrim.Bin101Value where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Bin.Value
open import Substrate.Foundation.Eq

bin-101-value : value (true ∷ false ∷ true ∷ []) ≡ 5
bin-101-value = refl
