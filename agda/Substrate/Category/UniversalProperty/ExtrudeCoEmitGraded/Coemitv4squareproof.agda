------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4squareproof
--
-- Defines: coemit-v4-square-proof
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4squareproof where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Transpose
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Daggerbar
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.ProofEq
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitproofeq
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- hence the V₄ square commutes at PROOF level (354 had only the head step): †∘bar and bar∘† agree everywhere.
coemit-v4-square-proof : {r s : RealTrace} (p : r ~ s) → ProofEq (transpose p) (dagger-bar p)
coemit-v4-square-proof p = coemit-proof-eq (transpose p) (dagger-bar p)
