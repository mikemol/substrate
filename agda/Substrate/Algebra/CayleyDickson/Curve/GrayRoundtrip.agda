------------------------------------------------------------------------
-- gray is invertible — a faithful (bijective) linearization of the F2^n index.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.GrayRoundtrip where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.CayleyDickson.Curve.Gray
open import Substrate.Algebra.CayleyDickson.Curve.GrayDecode
open import Substrate.Algebra.CayleyDickson.Curve.GrayDecodeStepGrayStep
open import Substrate.Foundation.Eq

gray-roundtrip : {n : ℕ} (b : Vec Bool n) → gray-decode (gray b) ≡ b
gray-roundtrip b = gray-decode′-gray′ false b
