------------------------------------------------------------------------
-- THE HILBERT (reflected-binary / Gray) curve: keep the top bit and XOR each
-- bit with the one above. Nothing sits above the top bit, so the seed is false.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.Gray where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Vec
open import Substrate.Algebra.CayleyDickson.Curve.GrayStep

gray : {n : ℕ} → Vec Bool n → Vec Bool n
gray = gray′ false
