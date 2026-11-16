------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitgraded
--
-- Defines: coemit-graded
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitgraded where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- THE INSTANCE: coemit-trace's grading is the finite-prefix chain (canonical GradedDivStr).
-- ⟡set1-paydown: the graded families (Vec ℕ = the prefix, const ℕ = the head digit)
-- are now GradedDivStr's params.
coemit-graded : GradedDivStr (Vec ℕ) (λ _ → ℕ)
coemit-graded = record
  { recon = λ _ v d → d ∷ v             -- grade-raising: extend the prefix by one digit
  }
