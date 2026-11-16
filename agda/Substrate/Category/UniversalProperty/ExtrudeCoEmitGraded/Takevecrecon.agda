------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Takevecrecon
--
-- Defines: take-vec-recon
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Takevecrecon where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitgraded
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Takevec
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (a) the graded prefix IS built by recon (grade-raising with the head digit) — definitional.
take-vec-recon : (n : ℕ) (r : RealTrace) → take-vec (suc n) r ≡ recon coemit-graded n (take-vec n (RealTrace.tail r)) (RealTrace.head r)
take-vec-recon n r = refl
