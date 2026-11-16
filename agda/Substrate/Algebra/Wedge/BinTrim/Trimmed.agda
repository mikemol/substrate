------------------------------------------------------------------------
-- The trimmed presentation: zero, or an EXACT width with a nonzero top
-- bit, the same value, and a proof the exact width fits the predicted one.
-- `fits` is the soundness statement (predicted ≥ actual).
-- Context: Substrate/Algebra/Wedge/BinTrim/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinTrim.Trimmed where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.Bin.Value
open import Substrate.Algebra.Wedge.BinTrim.Msb
open import Substrate.Foundation.Eq

data Trimmed {n : ℕ} (b : Bin n) : Set where
  is-zero  : value b ≡ zero → Trimmed b
  is-tight : (e : ℕ) (t : Bin (suc e))
           → suc e ≤ n            -- fits:     exact width within predicted
           → msb t ≡ true         -- tight:    no leading zero
           → value t ≡ value b    -- faithful: same numeral
           → Trimmed b
