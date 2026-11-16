------------------------------------------------------------------------
-- The LENGTH-grading of the F2^n index: the GENERIC length-graded vector carrier
-- (Wedge.VecGraded) instantiated at Bool — NOT a bespoke F2 grading.
-- Context: Substrate/Algebra/CayleyDickson/Grade/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Grade.F2LengthGrading where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.VecGraded.VecGraded

F₂-length-grading : GradedDivStr (Vec Bool) (λ _ → Bool)
F₂-length-grading = vec-graded Bool
