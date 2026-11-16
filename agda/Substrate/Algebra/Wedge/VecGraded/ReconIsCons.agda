------------------------------------------------------------------------
-- recon IS cons, definitionally.
-- Context: Substrate/Algebra/Wedge/VecGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.VecGraded.ReconIsCons where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.VecGraded.VecGraded
open import Substrate.Foundation.Eq

recon-is-cons : (A : Set) (n : ℕ) (v : Vec A n) (a : A) →
                recon (vec-graded A) n v a ≡ a ∷ v
recon-is-cons A n v a = refl
