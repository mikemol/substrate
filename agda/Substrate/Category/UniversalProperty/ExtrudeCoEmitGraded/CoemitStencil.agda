------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitStencil
--
-- Defines: CoemitStencil
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitStencil where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Bisim
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.Wedge.CrossMul
open import Substrate.Category.UniversalProperty.StencilAbstract
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceDivStr
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul


------------------------------------------------------------------------
-- coemit-stencil-abstract-instance + coemit-stencil-record (VERIFIED scoping, D-verify-dont-assume-substance):
-- StencilAbstract.StencilAgreement is GENERIC (params {A B R}, ⊗, ≈R, its refl/sym/trans) — coemit instantiates
-- it DIRECTLY: A=B=R=RealTrace, ⊗=trace-mul (the Π-typed mul), ≈R=~ (bisimilarity). The two framings AGREE when
-- their cross terms match up to ~ (= coherence). But FixpointStencilRecord.TwoFraming is over Fam (Idx D) with
-- Φ-step from TraceMuStep (Trace-SPECIFIC Kleene machinery) — RealTrace-DivStr doesn't drive Idx/Φ-step, so the
-- FULL TwoFraming record is HONEST-PARTIAL (documented); the ABSTRACT StencilAgreement IS the genuine instance.
------------------------------------------------------------------------

-- coemit's abstract stencil: the two framings are RealTrace legs, cross = trace-mul, agreement = up to ~.
module CoemitStencil = StencilAgreement {RealTrace} {RealTrace} {RealTrace}
                          trace-mul _~_ (λ {r} → ~-refl' r) ~-sym
