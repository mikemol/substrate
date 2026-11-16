------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitagreesalways
--
-- Defines: coemit-agrees-always
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitagreesalways where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemulcollapses
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitStencil
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitframed
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- coemit-agrees-is-bisim +F coemit-native-twoframing (operator's KEY: CrossMul is KLEIN-FOUR V₄ — swap A↔B +F
-- involution — a symmetry group modeled by the witness tower [V4Seam: rung-3→4 wedge quot=4=|V₄|, S₄=V₄⋊S₃], so
-- CrossMul is itself a SIMPLICIAL operator [trace-mul's square-zero d²=0 = SimplicialBoundary's ∂²=0]).
-- (1) The _agrees_ SWAP is one ℤ/2 of V₄. But square-zero (d²=0) TRIVIALIZES it: both cross terms collapse to z,
--     so ANY two framings agree (the μ/∂ side — coherence-everywhere). agrees is the V₄ swap, ∂²=0-trivialized.
-- (2) Bisimilarity is the SEPARATE ν content — the native two-framing: μ = the ∂/collapse (d²=0), ν = ~ (the gfp).
------------------------------------------------------------------------
-- (1) the swap symmetry (V₄'s ℤ/2) is ALWAYS satisfied — square-zero (∂²=0) trivializes agreement (μ/∂ side).
coemit-agrees-always : (a b : RealTrace) → CoemitStencil._agrees_ (coemit-framed a b) (coemit-framed b a)
coemit-agrees-always a b = ~-trans (trace-mul-collapses a a) (~-sym (trace-mul-collapses b b))
