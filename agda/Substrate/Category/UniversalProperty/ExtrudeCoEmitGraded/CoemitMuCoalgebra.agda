------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitMuCoalgebra
--
-- Defines: CoemitMuCoalgebra
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitMuCoalgebra where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Bisim.Cons
open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceDivStr
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3reaches
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectivefinite
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- coemit-mu-object + coemit-perspective-finite-rest + coemit-act-hom-full: the object-level completion of 335's
-- μ-coalgebra refinement. TraceKleeneColimit.Colim (μ=⋃ₙΦⁿ⊥) is over Fam (Idx D) with step-refinement — Trace-
-- SPECIFIC (RealTrace-DivStr doesn't drive Idx/step, like 329's TwoFraming), so the LITERAL Colim is honest-partial.
-- The GENUINE μ-object FOR COEMIT is the FINITE prefixes (take n r — the bounded/finite traces) carrying the
-- S₃-orbit coalgebra: a finite trace at depth n, projected per axis (perspective-finite), the axes S₃-connected.
------------------------------------------------------------------------
-- (1) coemit-mu-object: the μ-coalgebra — the finite (bounded-depth) projections + the orbit transition (s3-reaches).
--     carrier: a trace + a depth + an axis; project: the finite μ-view; transition: reach any other axis by S₃.
record CoemitMuCoalgebra : Set where
  field
    project    : GradingAxis → RealTrace → ℕ → List ℕ                          -- the finite μ-projection per axis
    transition : (a b : GradingAxis) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ a ≡ b)  -- the S₃-orbit coalgebra map
