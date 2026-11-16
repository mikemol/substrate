------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmulisboundarynu
--
-- Defines: coemit-mul-is-boundary-nu
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmulisboundarynu where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemulcollapses
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (3) coemit-mul-is-boundary: the two carriers' boundaries are identified UP TO the frame-GROUPOID (StencilGroupoid:
--     ν-frame = ~-groupoid, μ-frame = ≡-groupoid, connected by contractibility). trace-mul (ν-∂, square-zero → z)
--     and delAt-∂ (μ-∂, ∂²=0) are the SAME boundary via the groupoid iso — NOT literally equal (different carriers).
--     The witness: both square to the terminal (trace-mul → zero-trace; delAt pairs cancel) — the shared ∂²=0.
coemit-mul-is-boundary-nu : (r s : RealTrace) → trace-mul r s ~ zero-trace     -- ν-side ∂: square-zero (d²=0)
coemit-mul-is-boundary-nu = trace-mul-collapses
