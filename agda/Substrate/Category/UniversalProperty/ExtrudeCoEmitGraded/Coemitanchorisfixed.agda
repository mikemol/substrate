------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitanchorisfixed
--
-- Defines: coemit-anchor-is-fixed
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitanchorisfixed where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuunique
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- coemit-anchor-axis +F coemit-v4-acts-on-four +F coemit-retract-dual-grade +F coemit-s4iso-bridge.
-- CATALOG (context supplement, per item): Pairing = α-pair|β-pair|γ-pair — V₄'s THREE PARTITIONS OF THE 4 AXES (the
-- double-transpositions AS axis-pairings). C-orbit-canonical-decomposition: every signature = (orbit_key, v4_delta),
-- orbits indexed by Stab(D)-REPRESENTATIVES, v4_delta ∈ V₄. CY5: |OrbitKey| = 6, TotalSpace = Σ OrbitKey Fiber,
-- 6 × 4 = 24 = |S₄| — i.e. |S₄| = |S₃| · |V₄|, the ⋊ decomposition. S4Iso: TotalSpace ≃ S₄ (total-to-s4).
------------------------------------------------------------------------
-- (1) coemit-anchor-axis: the ANCHOR D is the FIXED point of the Stab(D)-action — the axis NOT permuted. In coemit,
--     the S₃-action (s3-on-axis) permutes the 3 GradingAxis; the anchor is the DISTINGUISHED, unmoved element. On the
--     trace side, zero-trace (μ, the least fixed point) is the unmoved point: every trace-mul product collapses TO it.
--     So: the anchor D ≙ the μ/zero-trace fixed point (the thing the action fixes), and C,S,W ≙ the 3 GradingAxis.
coemit-anchor-is-fixed : (r s : RealTrace) → trace-mul r s ~ zero-trace   -- the anchor point is what the action fixes
coemit-anchor-is-fixed = coemit-mu-unique
