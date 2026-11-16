------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittracekleindegenerate
--
-- Defines: coemit-trace-klein-degenerate
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittracekleindegenerate where

open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon3
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitTraceKlein
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)

-- and the DEGENERATE witness that the parameterization is inhabited (δ₂ = id: the V₂ collapse StarV4 warns of —
-- "over plain ℚ (conj = id) the twist is TRIVIAL — bar = id, so V₄ collapses back to V₂"). Honest: this shows the
-- module is non-empty; a GENUINE δ₂ (the carrier-level partner of †) remains open — ⟡coemit-trace-delta2.
coemit-trace-klein-degenerate : CommutingInvolutionsUpTo RealTrace _~_
coemit-trace-klein-degenerate =
  CoemitTraceKlein.coemit-trace-v4 (λ r → r) (λ r → ~-refl r) (λ r → ~-refl (bar r))
