------------------------------------------------------------------------
-- LOCALITY: on the hard Morton step (01 -> 10) Morton flips 2 bits.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.MortonJump where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Vec
open import Substrate.Algebra.CayleyDickson.Grade.Popcount
open import Substrate.Foundation.Eq

morton-jump : popcount (zipWith _xor_ (false ∷ true ∷ []) (true ∷ false ∷ [])) ≡ 2
morton-jump = refl
