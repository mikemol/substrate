------------------------------------------------------------------------
-- At a low grade Morton (Z-order) is cheaper.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.CrossoverLow where

open import Substrate.Algebra.Semiring.NatInf
open import Substrate.Algebra.CayleyDickson.Curve.Crossover
open import Substrate.Foundation.Eq

crossover-low : crossover (fin 2) (fin 4) ≡ fin 2
crossover-low = refl
