------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcrossmix
--
-- Defines: coemit-crossmix
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcrossmix where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Algebra.Wedge.CrossMul
open import Substrate.Algebra.Wedge.Bridge
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceDivStr
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceMulDivStr
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- coemit-crossmix-full: the FULL literal CrossMix on the DIAGONAL (A=B=RealTrace-DivStr, R=RealTrace-MulDivStr),
-- completing 326's partial fold now that trace-mul (the Π-typed mul, 327) exists. This is the DIAGONAL case of
-- StencilAbstract's cross pattern (the two framings A=≡/μ, B=~/ν as two legs of a cospan into R; here both legs
-- are RealTrace). embA=embB=id-bridge. Coherent cm r t = Nilpotent (cross = trace-mul r t) — and trace-mul
-- collapses to z (327), so the cross term is nilpotent at degree 1: coherence-everywhere (the μ/EXACT frame).
------------------------------------------------------------------------

-- the diagonal CrossMix: both legs RealTrace-DivStr, common carrier RealTrace-MulDivStr (the Π-typed threading).
coemit-crossmix : CrossMix RealTrace-DivStr RealTrace-DivStr RealTrace-MulDivStr
coemit-crossmix = record { embA = id-bridge RealTrace-DivStr ; embB = id-bridge RealTrace-DivStr }
