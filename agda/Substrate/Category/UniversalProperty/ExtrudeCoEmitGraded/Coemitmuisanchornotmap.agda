------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuisanchornotmap
--
-- Defines: coemit-mu-is-anchor-not-map
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuisanchornotmap where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble

open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuunique
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


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
