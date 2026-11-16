------------------------------------------------------------------------
-- Broadcast one multiplier bit across the multiplicand: `true` passes it
-- through, `false` masks it to zero. The AND-mask a hardware multiplier
-- performs — not a conditional.
-- Context: Substrate/Algebra/Wedge/BinMul/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinMul.Sel where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Bin.Carrier

sel : {n : ℕ} → Bool → Bin n → Bin n
sel a = map (a ∧_)
