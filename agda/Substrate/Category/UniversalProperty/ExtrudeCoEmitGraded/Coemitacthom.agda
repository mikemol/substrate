------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitacthom
--
-- Defines: coemit-act-hom
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitacthom where

open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (3) coemit-act-hom: the CARRIER is trace-mul = RealTrace acting on RealTrace via the coalgebraic morphism (the
--     COMPOSITION, not a single step). The action is a HOMOMORPHISM on the head-coalgebra: the mul's head is z-collapsed
--     (square-zero), so composing actions collapses coherently — the act-hom law on the ν-coalgebra structure.
coemit-act-hom : (r s t : RealTrace) → RealTrace.head (trace-mul (trace-mul r s) t) ≡ RealTrace.head (trace-mul r (trace-mul s t))
coemit-act-hom r s t = refl        -- both heads are 0 (square-zero); the composition-action is a head-homomorphism
