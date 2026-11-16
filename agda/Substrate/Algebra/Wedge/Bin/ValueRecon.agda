------------------------------------------------------------------------
-- THE CO-APEX: the graded reconstruction IS the radix-2 Horner step.
-- Holds by `refl` for VARIABLE n, bs, b — nothing to discharge.
-- Context: Substrate/Algebra/Wedge/Bin/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Bin.ValueRecon where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.Bin.BinGraded
open import Substrate.Algebra.Wedge.Bin.Value
open import Substrate.Foundation.Eq

value-recon : (n : ℕ) (bs : Bin n) (b : Bool) →
              value (recon bin-graded n bs b) ≡ boolToℕ b ℕ+ (value bs ℕ+ value bs)
value-recon _ _ _ = refl
