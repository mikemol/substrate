------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitTraceKlein
--
-- Defines: CoemitTraceKlein
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitTraceKlein where

open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon3
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Axes.Axis

open import Substrate.Groups.Symmetric.Eq Axis
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitconjconj
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- INSTANCE 2 (≈ := ~): RealTrace, with δ₁ = bar. The SECOND involution is a MODULE PARAMETER, not a postulate:
-- give any ~-involutive δ₂ commuting with bar, and coemit's carrier carries the Klein four-group.
module CoemitTraceKlein
  (δ₂       : RealTrace → RealTrace)
  (δ₂-inv   : (r : RealTrace) → δ₂ (δ₂ r) ~ r)
  (δ₂-comm  : (r : RealTrace) → δ₂ (bar r) ~ bar (δ₂ r))
  where

  coemit-trace-v4 : CommutingInvolutionsUpTo RealTrace _~_
  coemit-trace-v4 = record
    { δ₁ = bar ; δ₂ = δ₂
    ; δ₁-inv = coemit-conj-conj ; δ₂-inv = δ₂-inv ; commute = δ₂-comm }
