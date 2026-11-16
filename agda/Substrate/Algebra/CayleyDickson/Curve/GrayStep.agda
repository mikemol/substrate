------------------------------------------------------------------------
-- The Gray encoding step: thread the bit above.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.GrayStep where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Vec

gray′ : {n : ℕ} → Bool → Vec Bool n → Vec Bool n
gray′ prev []       = []
gray′ prev (b ∷ bs) = (prev xor b) ∷ gray′ b bs
