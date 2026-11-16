------------------------------------------------------------------------
-- a = 2·q ℕ+ r at the value level, for a VARIABLE numeral.
-- Context: Substrate/Algebra/Wedge/Bin/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Bin.BinDivmod2Value where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.Bin.Value
open import Substrate.Algebra.Wedge.Bin.BinQuot
open import Substrate.Algebra.Wedge.Bin.BinRem
open import Substrate.Foundation.Eq

bin-divmod2-value :
  (n : ℕ) (a : Bin (suc n)) →
  value a ≡ boolToℕ (bin-rem n a) ℕ+ (value (bin-quot a) ℕ+ value (bin-quot a))
bin-divmod2-value _ (_ ∷ _) = refl
