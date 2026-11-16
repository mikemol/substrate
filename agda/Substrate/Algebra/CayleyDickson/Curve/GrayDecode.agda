------------------------------------------------------------------------
-- Gray decoding, seeded at false.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.GrayDecode where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Vec
open import Substrate.Algebra.CayleyDickson.Curve.GrayDecodeStep

gray-decode : {n : ℕ} → Vec Bool n → Vec Bool n
gray-decode = gray-decode′ false
