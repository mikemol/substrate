------------------------------------------------------------------------
-- The cell read of the uncons wedge is the shed head.
-- Context: Substrate/Algebra/Wedge/VecGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.VecGraded.VecCell where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.VecGraded.VecStep
open import Substrate.Foundation.Eq

vec-cell : (A : Set) (n : ℕ) (v : Vec A n) (a : A) →
           gcell (vec-step A n v a) ≡ a
vec-cell A n v a = refl
