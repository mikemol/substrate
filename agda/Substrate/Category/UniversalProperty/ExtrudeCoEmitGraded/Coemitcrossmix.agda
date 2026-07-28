------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcrossmix
--
-- Defines: coemit-crossmix
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcrossmix where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Final
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.Wedge
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.Wedge.CrossMul
open import Substrate.Algebra.Wedge.Bridge
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceDivStr
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceMulDivStr


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
