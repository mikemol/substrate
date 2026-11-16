------------------------------------------------------------------------
-- The zero numeral at a given width.
-- Context: Substrate/Algebra/Wedge/BinMul/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinMul.Zeros where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Bin.Carrier

zeros : (n : ℕ) → Bin n
zeros n = replicate n false
