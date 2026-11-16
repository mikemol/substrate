------------------------------------------------------------------------
-- The radix-2 remainder: the shed head bit, read off the graded wedge.
-- Context: Substrate/Algebra/Wedge/Bin/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Bin.BinRem where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.Bin.BinDivmod2

bin-rem : (n : ℕ) (a : Bin (suc n)) → Bool
bin-rem n a = gcell (bin-divmod2 n a)
