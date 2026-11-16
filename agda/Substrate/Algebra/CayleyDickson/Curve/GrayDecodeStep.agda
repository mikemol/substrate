------------------------------------------------------------------------
-- The Gray decoding step: thread the running parity.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.GrayDecodeStep where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Vec

gray-decode′ : {n : ℕ} → Bool → Vec Bool n → Vec Bool n
gray-decode′ acc []       = []
gray-decode′ acc (g ∷ gs) = (acc xor g) ∷ gray-decode′ (acc xor g) gs
