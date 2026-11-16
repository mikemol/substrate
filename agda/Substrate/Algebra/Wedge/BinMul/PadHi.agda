------------------------------------------------------------------------
-- Widen at the HIGH end by appending zeros. LSB-first, so appending
-- cannot change the value.
-- Context: Substrate/Algebra/Wedge/BinMul/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinMul.PadHi where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.BinMul.Zeros

padHi : {n : ℕ} (k : ℕ) → Bin n → Bin (n ℕ+ k)
padHi k b = b ++ zeros k
