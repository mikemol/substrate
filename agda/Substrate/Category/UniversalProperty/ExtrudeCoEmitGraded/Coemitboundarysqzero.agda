------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitboundarysqzero
--
-- Defines: coemit-boundary-sq-zero
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitboundarysqzero where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemulcollapses
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- (1) coemit-v4-simplicial-literal: trace-mul's square-zero IS the simplicial ∂²=0 shape. SimplicialBoundary's
-- law is delAt i (delAt (suc j) xs) ≡ delAt j (delAt i xs) (∂∘∂=0); trace-mul r s collapses to z (d²=0) — the
-- same square-zero/boundary structure. Here: trace-mul-collapses witnesses the ∂²=0-shape on the trace carrier.
------------------------------------------------------------------------
-- the boundary square-zero on traces: applying trace-mul (the ∂) twice collapses to z (the ∂²=0 shape, up to ~).
coemit-boundary-sq-zero : (r s : RealTrace) → trace-mul (trace-mul r s) (trace-mul r s) ~ zero-trace
coemit-boundary-sq-zero r s = trace-mul-collapses (trace-mul r s) (trace-mul r s)
