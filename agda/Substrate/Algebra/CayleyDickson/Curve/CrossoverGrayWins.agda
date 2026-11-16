------------------------------------------------------------------------
-- The crossover, fed the REAL curve costs (no longer hand-picked), picks Gray.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.CrossoverGrayWins where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Semiring.NatInf
open import Substrate.Algebra.CayleyDickson.Grade.Popcount
open import Substrate.Algebra.CayleyDickson.Curve.Gray
open import Substrate.Algebra.CayleyDickson.Curve.Crossover
open import Substrate.Foundation.Eq

crossover-gray-wins :
  crossover (fin (popcount (zipWith _xor_ (false ∷ true ∷ []) (true ∷ false ∷ []))))
            (fin (popcount (zipWith _xor_ (gray (false ∷ true ∷ [])) (gray (true ∷ false ∷ [])))))
  ≡ fin 1
crossover-gray-wins = refl
