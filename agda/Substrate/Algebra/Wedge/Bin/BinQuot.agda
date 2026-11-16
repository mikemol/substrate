------------------------------------------------------------------------
-- The radix-2 quotient: the tail (dropping the least significant bit).
-- Context: Substrate/Algebra/Wedge/Bin/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Bin.BinQuot where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Bin.Carrier

bin-quot : {n : ℕ} → Bin (suc n) → Bin n
bin-quot = tail
