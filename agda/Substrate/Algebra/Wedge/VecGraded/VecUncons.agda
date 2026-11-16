------------------------------------------------------------------------
-- Every nonempty vector IS its head consed on its tail — the uncons wedge.
-- Total, refl, no certificate.
-- Context: Substrate/Algebra/Wedge/VecGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.VecGraded.VecUncons where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.VecGraded.VecGraded
open import Substrate.Foundation.Eq

vec-uncons : (A : Set) (n : ℕ) (v : Vec A (suc n)) →
             GradedWedge (vec-graded A) n v (tail v)
vec-uncons A n (a ∷ v) = record { rem = a ; wedge-eq = refl }
