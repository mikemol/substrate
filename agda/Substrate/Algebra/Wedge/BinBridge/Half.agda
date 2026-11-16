------------------------------------------------------------------------
-- Division of a ℕ by the radix, stepping TWO at a time. See Odd.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.Half where

open import Substrate.Foundation.Nat.Nat

half : ℕ → ℕ
half zero          = zero
half (suc zero)    = zero
half (suc (suc n)) = suc (half n)
