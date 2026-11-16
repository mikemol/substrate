------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdaggeronproofs
--
-- Defines: coemit-dagger-on-proofs
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdaggeronproofs where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- †  and bar act on DIFFERENT arguments († on the ~-proof, bar on the step-chirality), hence they COMMUTE —
-- the V₄-not-dihedral condition (StarV4's recip-bar). ⟨†, bar⟩ ≅ ℤ/2 × ℤ/2.
coemit-dagger-on-proofs : {r s : RealTrace} → r ~ s → s ~ r
coemit-dagger-on-proofs = ~-sym
