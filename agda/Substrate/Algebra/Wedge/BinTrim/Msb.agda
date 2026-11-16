------------------------------------------------------------------------
-- The most significant bit. `Bin` is LSB-first, so the MSB is the LAST
-- element; matching on the index makes `msb (b ∷ t) = msb t` definitional.
-- Context: Substrate/Algebra/Wedge/BinTrim/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinTrim.Msb where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Bin.Carrier

msb : {n : ℕ} → Bin (suc n) → Bool
msb {zero}  (b ∷ _)  = b
msb {suc _} (_ ∷ bs) = msb bs
