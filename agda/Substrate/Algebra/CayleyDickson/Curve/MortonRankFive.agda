------------------------------------------------------------------------
-- Witness: the index 1*2^0 + 0*2^1 + 1*2^2 has Morton rank 5.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.MortonRankFive where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Algebra.CayleyDickson.Curve.Morton
open import Substrate.Foundation.Eq

morton-rank-five : morton (true ∷ false ∷ true ∷ []) ≡ 5
morton-rank-five = refl
