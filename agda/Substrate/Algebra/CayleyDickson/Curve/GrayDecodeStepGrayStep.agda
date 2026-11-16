------------------------------------------------------------------------
-- Decoding inverts encoding, threading any seed.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.GrayDecodeStepGrayStep where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Vec
open import Substrate.Algebra.CayleyDickson.Curve.GrayStep
open import Substrate.Algebra.CayleyDickson.Curve.GrayDecodeStep
open import Substrate.Algebra.CayleyDickson.Curve.XorCancelL
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong

gray-decode′-gray′ : {n : ℕ} (p : Bool) (bs : Vec Bool n) → gray-decode′ p (gray′ p bs) ≡ bs
gray-decode′-gray′ p []       = refl
gray-decode′-gray′ p (b ∷ bs) rewrite xor-cancelˡ p b = cong (b ∷_) (gray-decode′-gray′ b bs)
