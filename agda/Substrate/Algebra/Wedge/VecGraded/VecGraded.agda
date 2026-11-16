------------------------------------------------------------------------
-- Vec A as a GRADED wedge-carrier: C n = Vec A n, R n = A, recon = cons.
-- Building a vector IS the graded free construction.
-- Context: Substrate/Algebra/Wedge/VecGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.VecGraded.VecGraded where

open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Graded

vec-graded : (A : Set) → GradedDivStr (Vec A) (λ _ → A)
vec-graded A = record { recon = λ n v a → a ∷ v }
