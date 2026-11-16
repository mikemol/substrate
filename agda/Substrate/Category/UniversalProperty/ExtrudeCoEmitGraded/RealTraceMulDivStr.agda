------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceMulDivStr
--
-- Defines: RealTrace-MulDivStr
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceMulDivStr where

open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceDivStr
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


RealTrace-MulDivStr : MulDivStr RealTrace
RealTrace-MulDivStr = record { base = RealTrace-DivStr ; mul = trace-mul }
