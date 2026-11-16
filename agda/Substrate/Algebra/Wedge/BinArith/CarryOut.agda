------------------------------------------------------------------------
-- The bit falling off the top: the other PROJECTION of addU's single
-- traversal. Kept out-of-band, which is the add-width law (max + 1).
-- Context: Substrate/Algebra/Wedge/BinArith/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinArith.CarryOut where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.BinArith.AddU

carryOut : {n : ℕ} → Bool → Bin n → Bin n → Bool
carryOut c as bs = proj₂ (addU c as bs)
