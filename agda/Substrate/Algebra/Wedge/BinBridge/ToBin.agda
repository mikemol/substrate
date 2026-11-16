------------------------------------------------------------------------
-- THE ENCODER — the run-shaped radix unfold, fuelled by the PREDICTED
-- width. Each step sheds one bit and halves the residue; when the fuel
-- runs out the remaining high bits are truncated (see ToBinValue for the
-- bound that makes the encoding exact). This is where the unary spine is
-- walked, and it is walked once.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.ToBin where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.BinBridge.Odd
open import Substrate.Algebra.Wedge.BinBridge.Half

toBin : (w : ℕ) → ℕ → Bin w
toBin zero    _ = []
toBin (suc w) n = odd n ∷ toBin w (half n)
