------------------------------------------------------------------------
-- The crossover is a TROPICAL (min-cost) selection: of two curves' costs it
-- takes the cheaper — exactly the tropical (+) = min on N-infinity. The chosen
-- curve at a grade is the argmin; the crossover boundary is where it flips.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.Crossover where

open import Substrate.Algebra.Semiring.NatInf

crossover : ℕ∞ → ℕ∞ → ℕ∞
crossover = _⊓_
