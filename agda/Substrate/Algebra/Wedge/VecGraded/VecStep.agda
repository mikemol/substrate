------------------------------------------------------------------------
-- The canonical graded step: a ∷ v wedges against v, shedding head a as the residue.
-- Context: Substrate/Algebra/Wedge/VecGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.VecGraded.VecStep where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.VecGraded.VecGraded
open import Substrate.Foundation.Eq

vec-step : (A : Set) (n : ℕ) (v : Vec A n) (a : A) →
           GradedWedge (vec-graded A) n (a ∷ v) v
vec-step A n v a = record { rem = a ; wedge-eq = refl }
