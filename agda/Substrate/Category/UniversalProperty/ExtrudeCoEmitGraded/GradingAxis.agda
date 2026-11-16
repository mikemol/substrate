------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
--
-- Defines: GradingAxis
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- (2) coemit-s3-on-v4: V₄'s THREE involutions = the THREE grading axes (311). S₃ permutes them (the ⋊ in
-- S₄=V₄⋊S₃). The three axes, each an involution (self-inverse flip), enumerated as a 3-element index S₃ acts on.
------------------------------------------------------------------------
data GradingAxis : Set where
  μν-axis        : GradingAxis   -- axis 1: μ (finite/exact) ↔ ν (coinductive/up-to) — the FixpointStencil frame
  head-tail-axis : GradingAxis   -- axis 2: head (this digit) ↔ tail (the rest) — the coalgebra decomposition
  cyc-aper-axis  : GradingAxis   -- axis 3: cyclic (collapses/period) ↔ aperiodic (the obstruction) — cover-the-cycle
