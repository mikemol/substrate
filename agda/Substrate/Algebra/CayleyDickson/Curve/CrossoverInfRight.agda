------------------------------------------------------------------------
-- Infinity (unreachable) is the cost identity: a curve with no cost never
-- wins a crossover.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.CrossoverInfRight where

open import Substrate.Algebra.Semiring.NatInf
open import Substrate.Algebra.CayleyDickson.Curve.Crossover
open import Substrate.Foundation.Eq

crossover-∞ʳ : crossover (fin 3) ∞ ≡ fin 3
crossover-∞ʳ = refl
