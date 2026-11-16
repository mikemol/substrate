------------------------------------------------------------------------
-- The Morton / Z-order linearization: the F2^n index -> its rank (LSB-first
-- binary value SUM bit_i*2^i, written as repeated doubling so no * is needed).
-- Traversing indices in increasing rank IS the Morton curve.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.Morton where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Vec
open import Substrate.Algebra.CayleyDickson.Grade.Bit

morton : {n : ℕ} → Vec Bool n → ℕ
morton []       = zero
morton (b ∷ bs) = bit b ℕ+ (morton bs ℕ+ morton bs)
