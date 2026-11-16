------------------------------------------------------------------------
-- An n-bit binary numeral, LEAST significant bit first (morton's order).
-- Context: Substrate/Algebra/Wedge/Bin/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Bin.Carrier where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec

Bin : ℕ → Set
Bin = Vec Bool
