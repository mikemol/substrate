------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitacthomfull
--
-- Defines: coemit-act-hom-full
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitacthomfull where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemulcollapses
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (3) coemit-act-hom-full: trace-mul's FULL associativity up to ~ (not just heads). Both nestings collapse to
--     zero-trace (square-zero), so they are ~ by transitivity through zero-trace — the composition-carrier's assoc.
coemit-act-hom-full : (r s t : RealTrace) → trace-mul (trace-mul r s) t ~ trace-mul r (trace-mul s t)
coemit-act-hom-full r s t = ~-trans (trace-mul-collapses (trace-mul r s) t)
                                     (~-sym (trace-mul-collapses r (trace-mul s t)))
