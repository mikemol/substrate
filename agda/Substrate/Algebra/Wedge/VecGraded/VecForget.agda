------------------------------------------------------------------------
-- The forgetful read of the uncons wedge recovers the vector.
-- Context: Substrate/Algebra/Wedge/VecGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.VecGraded.VecForget where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.VecGraded.VecStep
open import Substrate.Foundation.Eq

vec-forget : (A : Set) (n : ℕ) (v : Vec A n) (a : A) →
             gforget (vec-step A n v a) ≡ a ∷ v
vec-forget A n v a = refl
