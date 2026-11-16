------------------------------------------------------------------------
-- The low bit of a ℕ, stepping TWO at a time. Paired with `half`: they are
-- one division by the radix and must share a recursion shape, or their
-- joint law (Divmod2) is not a three-case induction.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.Odd where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat

odd : ℕ → Bool
odd zero          = false
odd (suc zero)    = true
odd (suc (suc n)) = odd n
