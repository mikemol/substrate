------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitStencil
--
-- Defines: CoemitStencil
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitStencil where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Bisim.Cons
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.StencilAbstract
open import Substrate.Algebra.R.Trace.Bisim.Refl
  renaming (~-refl to ~-refl')
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceDivStr
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- coemit-stencil-abstract-instance +F coemit-stencil-record (VERIFIED scoping, D-verify-dont-assume-substance):
-- StencilAbstract.StencilAgreement is GENERIC (params {A B R}, ⊗, ≈R, its refl/sym/trans) — coemit instantiates
-- it DIRECTLY: A=B=R=RealTrace, ⊗=trace-mul (the Π-typed mul), ≈R=~ (bisimilarity). The two framings AGREE when
-- their cross terms match up to ~ (= coherence). But FixpointStencilRecord.TwoFraming is over Fam (Idx D) with
-- Φ-step from TraceMuStep (Trace-SPECIFIC Kleene machinery) — RealTrace-DivStr doesn't drive Idx/Φ-step, so the
-- FULL TwoFraming record is HONEST-PARTIAL (documented); the ABSTRACT StencilAgreement IS the genuine instance.
------------------------------------------------------------------------

-- coemit's abstract stencil: the two framings are RealTrace legs, cross = trace-mul, agreement = up to ~.
module CoemitStencil = StencilAgreement {RealTrace} {RealTrace} {RealTrace}
                          trace-mul _~_ (λ {r} → ~-refl' r) ~-sym
