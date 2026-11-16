------------------------------------------------------------------------
-- The ANF degree = Hamming weight of an F2^n index.
-- Context: Substrate/Algebra/CayleyDickson/Grade/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Grade.Popcount where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.CayleyDickson.Grade.Bit

popcount : {n : ℕ} → Vec Bool n → ℕ
popcount []       = zero
popcount (b ∷ bs) = bit b ℕ+ popcount bs
