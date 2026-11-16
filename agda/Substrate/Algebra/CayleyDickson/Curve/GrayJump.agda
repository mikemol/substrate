------------------------------------------------------------------------
-- LOCALITY: the Gray-encoded step flips 1 bit — the reflected curve preserves
-- locality, and these popcount jumps are the crossover's real costs.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.GrayJump where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Vec
open import Substrate.Algebra.CayleyDickson.Grade.Popcount
open import Substrate.Algebra.CayleyDickson.Curve.Gray
open import Substrate.Foundation.Eq

gray-jump : popcount (zipWith _xor_ (gray (false ∷ true ∷ [])) (gray (true ∷ false ∷ []))) ≡ 1
gray-jump = refl
