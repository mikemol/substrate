------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittracev4genuine
--
-- Defines: coemit-trace-v4-genuine
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittracev4genuine where

open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon3
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitTraceKlein
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbarinvol
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbarbarcommute
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- THE GENUINE V₄ ON THE TRACE CARRIER (CoemitTraceKlein's parameters, discharged — NOT the degenerate id).
coemit-trace-v4-genuine : CommutingInvolutionsUpTo RealTrace _~_
coemit-trace-v4-genuine =
  CoemitTraceKlein.coemit-trace-v4 bar₂ coemit-bar₂-invol coemit-bar-bar₂-commute
