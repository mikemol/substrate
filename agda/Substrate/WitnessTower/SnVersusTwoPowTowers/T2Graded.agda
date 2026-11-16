------------------------------------------------------------------------
-- Ⓣ₂ — the Cayley-Dickson doubling tower's basis grading as a GradedDivStr; the
-- increment is one bit = one doubling. Cited from its home, not rebuilt.
-- Context: Substrate/WitnessTower/SnVersusTwoPowTowers/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SnVersusTwoPowTowers.T2Graded where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.CayleyDickson.Grade.F2LengthGrading

Ⓣ₂-graded : GradedDivStr (Vec Bool) (λ _ → Bool)
Ⓣ₂-graded = F₂-length-grading
