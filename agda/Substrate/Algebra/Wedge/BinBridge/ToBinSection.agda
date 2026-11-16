------------------------------------------------------------------------
-- THE RETRACTION — every numeral is the encoding of its own value.
-- Structural on the bits, so no bound is needed: the width is given.
-- This says the bit carrier holds no junk.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.ToBinSection where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.Bin.Value
open import Substrate.Algebra.Wedge.BinBridge.ToBin
open import Substrate.Algebra.Wedge.BinBridge.OddDouble
open import Substrate.Algebra.Wedge.BinBridge.HalfDouble
open import Substrate.Algebra.Wedge.BinBridge.OddSucDouble
open import Substrate.Algebra.Wedge.BinBridge.HalfSucDouble
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Trans

toBin-section : {w : ℕ} (b : Bin w) → toBin w (value b) ≡ b
toBin-section []                   = refl
toBin-section {suc w} (false ∷ bs) =
  cong₂ _∷_ (odd-double (value bs))
            (trans (cong (toBin w) (half-double (value bs))) (toBin-section bs))
toBin-section {suc w} (true ∷ bs) =
  cong₂ _∷_ (odd-suc-double (value bs))
            (trans (cong (toBin w) (half-suc-double (value bs))) (toBin-section bs))
