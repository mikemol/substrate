------------------------------------------------------------------------
-- Division BY THE RADIX: total, certificate definitional. Cited, not
-- built — this is `vec-uncons`; the quotient is the tail.
-- Context: Substrate/Algebra/Wedge/Bin/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Bin.BinDivmod2 where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.VecGraded.VecUncons
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.Bin.BinGraded

bin-divmod2 : (n : ℕ) (a : Bin (suc n)) → GradedWedge bin-graded n a (tail a)
bin-divmod2 = vec-uncons Bool
