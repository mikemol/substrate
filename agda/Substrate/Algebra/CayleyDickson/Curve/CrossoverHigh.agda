------------------------------------------------------------------------
-- At a high grade Hilbert (locality) wins — the argmin, hence the curve, flips.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.CrossoverHigh where

open import Substrate.Algebra.Semiring.NatInf
open import Substrate.Algebra.CayleyDickson.Curve.Crossover
open import Substrate.Foundation.Eq

crossover-high : crossover (fin 8) (fin 6) ≡ fin 6
crossover-high = refl
