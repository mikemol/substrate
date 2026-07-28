------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitagreesalways
--
-- Defines: coemit-agrees-always
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitagreesalways where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Bisim
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Product
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
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
open import Substrate.Groups.V4.Bijection
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemulcollapses
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitStencil
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitframed


------------------------------------------------------------------------
-- coemit-agrees-is-bisim + coemit-native-twoframing (operator's KEY: CrossMul is KLEIN-FOUR V₄ — swap A↔B +
-- involution — a symmetry group modeled by the witness tower [V4Seam: rung-3→4 wedge quot=4=|V₄|, S₄=V₄⋊S₃], so
-- CrossMul is itself a SIMPLICIAL operator [trace-mul's square-zero d²=0 = SimplicialBoundary's ∂²=0]).
-- (1) The _agrees_ SWAP is one ℤ/2 of V₄. But square-zero (d²=0) TRIVIALIZES it: both cross terms collapse to z,
--     so ANY two framings agree (the μ/∂ side — coherence-everywhere). agrees is the V₄ swap, ∂²=0-trivialized.
-- (2) Bisimilarity is the SEPARATE ν content — the native two-framing: μ = the ∂/collapse (d²=0), ν = ~ (the gfp).
------------------------------------------------------------------------
-- (1) the swap symmetry (V₄'s ℤ/2) is ALWAYS satisfied — square-zero (∂²=0) trivializes agreement (μ/∂ side).
coemit-agrees-always : (a b : RealTrace) → CoemitStencil._agrees_ (coemit-framed a b) (coemit-framed b a)
coemit-agrees-always a b = ~-trans (trace-mul-collapses a a) (~-sym (trace-mul-collapses b b))
