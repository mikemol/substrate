------------------------------------------------------------------------
-- The ripple adder as ONE unfold: emit the sum bit, bleed the carry.
-- The carry IS the residue, the sum bit IS the per-step observation, the
-- vector length IS the fuel — mirroring Wedge.Coalgebra.run's own
-- emit-and-residue line. A first draft split this into two spine-walks,
-- each RECOMPUTING the whole carry chain; that is the anti-pattern this
-- migration exists to remove.
-- Context: Substrate/Algebra/Wedge/BinArith/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinArith.AddU where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.Or
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Product
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.BinArith.SumBit
open import Substrate.Algebra.Wedge.BinArith.CarryBit

addU : {n : ℕ} → Bool → Bin n → Bin n → Bin n × Bool
addU c []       []       = [] , c
addU c (a ∷ as) (b ∷ bs) =
  let r = addU (carryBit c a b) as bs
  in sumBit c a b ∷ proj₁ r , proj₂ r
