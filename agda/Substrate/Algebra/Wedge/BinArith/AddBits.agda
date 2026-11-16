------------------------------------------------------------------------
-- The result bits: a PROJECTION of addU's single traversal, never a
-- second walk of the spine.
-- Context: Substrate/Algebra/Wedge/BinArith/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinArith.AddBits where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.BinArith.AddU

addBits : {n : ℕ} → Bool → Bin n → Bin n → Bin n
addBits c as bs = proj₁ (addU c as bs)
