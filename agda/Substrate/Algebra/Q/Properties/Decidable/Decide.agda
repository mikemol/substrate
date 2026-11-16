------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Decidable.Decide
--
-- Dec (a ≈ℚ b), from reduce-eq? plus the bridge both ways.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Decidable.Decide where

open import Substrate.Foundation.Negation.Dec
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
open import Substrate.Algebra.Q.Properties.Canonical.ReduceRespectsApprox
open import Substrate.Algebra.Q.Properties.Decidable.ReduceEq
open import Substrate.Algebra.Q.Properties.Decidable.Bridge

_≈ℚ?_ : (a b : ℚ) → Dec (a ≈ℚ b)
a ≈ℚ? b with reduce-eq? a b
... | yes re = yes (re→≈ re)
... | no ¬re = no (λ a≈b → ¬re (reduce-respects-≈ a≈b))
