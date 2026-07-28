------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuisanchornotmap
--
-- Defines: coemit-mu-is-anchor-not-map
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuisanchornotmap where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Bisim
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.Wedge
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
open import Substrate.Groups.V4.Bijection
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2
open import Substrate.Cocycles.V4Signature.S4Iso.Anchor
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Cocycles.V4Signature.S4Iso.Classify
open import Substrate.Axes.Axis

open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Axes.VOfAxis
open import Substrate.Axes.AxisOfV
open import Substrate.Axes.ActAxis
open import Substrate.Groups.SemidirectProduct.V
open import Substrate.Groups.SemidirectProduct.S
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuunique


------------------------------------------------------------------------
-- coemit-mu-is-D + coemit-v4-component + coemit-total-to-s4 (the loose ends).
-- CATALOG (per item): **Substrate.Axes: "Axis is a V₄-torsor anchored at D"** — v-of-axis D = e (the IDENTITY),
-- C = α, S = β, W = γ; act-axis v x = axis-of-v (v V4.· v-of-axis x). So act-axis v D = axis-of-v v: **D is the
-- torsor's BASEPOINT, the axis sitting at V₄'s identity**. That is WHY D is the anchor (Stab(D), the rigidification).
-- S4Iso/Classify: total-to-s4 (ok , v) = embed v · orbit-key-to-stab-d ok (the ⋊-product); s4-to-total the reverse.
-- SemidirectProduct: v-for : Permutation → V₄; s-for : Permutation → Permutation; s-for-fixes-anchor (σ = v·s).
------------------------------------------------------------------------
-- (1) coemit-mu-is-D (HONEST: a STRUCTURAL correspondence, NOT a map — μ : RealTrace, D : Axis are different types).
--     D is the axis at V₄'s IDENTITY (v-of-axis D = e); μ = zero-trace is the composition-carrier's LEAST fixed point
--     (every trace-mul product collapses to it). Both are their structure's NEUTRAL/anchor element:
--       • D  : the V₄-torsor basepoint  — act-axis v D = axis-of-v v  (the identity's orbit-point)
--       • μ  : the trace-mul absorber   — trace-mul r s ~ zero-trace  (the collapse point)
--     NOTE the honest asymmetry: D is a torsor IDENTITY (neutral); μ is an ABSORBING element (zero). They occupy the
--     same *anchoring* role (what Stab fixes / what the action collapses to), but are NOT the same algebraic notion.
coemit-mu-is-anchor-not-map : (r s : RealTrace) → trace-mul r s ~ zero-trace   -- μ absorbs (the coemit-side anchor)
coemit-mu-is-anchor-not-map = coemit-mu-unique
