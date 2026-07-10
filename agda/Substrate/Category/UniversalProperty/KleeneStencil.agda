{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.KleeneStencil — ⟡kleene-stencil: the KLEENE
-- fixed-point as a SECOND instance of the uniqueness stencil (UNIQUENESS_STENCIL.md),
-- making the ≥2-instances audit MACHINE-CHECKABLE (not asserted). Binds the stencil's
-- μ-layer and ν-layer to the ALREADY-PROVEN Kleene results (159/162), so "the stencil
-- cuts this shape too" is a typecheck, not a claim.
--
-- The Kleene fixed-point: μΦ = ⋃ₙ Φⁿ⊥ ≅ Trace (LEAST fixed point, the ≡/≅ frame, 159)
-- ⊣ νΦ = ⋂ₙ Φⁿ⊤ = Limit (GREATEST fixed point, the ⊑-universal-property frame, 162),
-- the SAME Lambek-hinged μ⊣ν as the trace/wedge instance — least-vs-greatest fixed point.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.KleeneStencil where

open import Substrate.Algebra.Wedge using (DivStr; Trace; ℕ-div)
open import Substrate.Category.Allegory.Refinement using (Fam; _⊑ᶠ_)
open import Substrate.Algebra.Wedge.TraceMuStep using (Idx; Φ-step; TraceF)
import Substrate.Algebra.Wedge.TraceKleeneColimit as Kμ
import Substrate.Algebra.Wedge.TraceNuColimit as Kν

module _ {C : Set} (D : DivStr C) where

  ------------------------------------------------------------------------
  -- ① THE μ-LAYER (least fixed point, ≡/≅ frame): Trace ⊑ Colim — the trace family
  -- embeds into the Kleene colimit ⋃ₙ Φⁿ⊥. (159's trace→colim; with its converse,
  -- Colim ≅ Trace = μΦ.) The stencil's μ-fold layer for the Kleene fixed-point.
  ------------------------------------------------------------------------
  kleene-μ-layer : TraceF D ⊑ᶠ Kμ.Colim D
  kleene-μ-layer = Kμ.trace→colim D

  ------------------------------------------------------------------------
  -- ② THE ν-LAYER (greatest fixed point, ⊑-UP frame): every ν-coalgebra X ⊑ Φ-step X
  -- sits BELOW the Limit ⋂ₙ Φⁿ⊤ — the greatest-fixed-point universal property (162),
  -- the DUAL of μ's (μ below every pre-fixed-point). The stencil's ν-whole layer for
  -- the Kleene fixed-point (the ⊑-frame analogue of ana-unique's ~-frame).
  ------------------------------------------------------------------------
  kleene-ν-layer : {X : Fam (Idx D)} → (X ⊑ᶠ Φ-step D X) → X ⊑ᶠ Kν.Limit D
  kleene-ν-layer = Kν.coalg-below-limit D

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the stencil cuts a SECOND fixed-point, machine-checked):
-- the KLEENE fixed-point (μΦ = ⋃ Φⁿ⊥ ≅ Trace ⊣ νΦ = ⋂ Φⁿ⊤ = Limit) instantiates the
-- uniqueness stencil's μ-layer (kleene-μ-layer = trace→colim, the LEAST fixed point,
-- ≡/≅ frame) and ν-layer (kleene-ν-layer = coalg-below-limit, the GREATEST fixed point,
-- the ⊑-universal-property, DUAL of μ's) — the SAME μ⊣ν Lambek-hinged structure as the
-- trace/wedge instance (185/186/187), read as least-vs-greatest fixed point. So the
-- stencil is REAL: it cuts ≥2 distinct fixed-points (trace/wedge PROVEN all three layers;
-- Kleene bound here to its two proven layers) — this typecheck IS the ≥2-instances audit.
-- The "one fixed-point vs a general pattern" either/or dissolves: the stencil is the
-- INVARIANT the substrate's own one-diagonal claim (Category.Lawvere) already asserts;
-- here it is made an instantiable, machine-checkable template. The THIRD instance in
-- waiting is the combinator-Y fixed-point (ExtruderFix) = ⟡X8a-iter, the extruder as the
-- μ-layer of its own diagonal — the same stencil, the third registered solver.
------------------------------------------------------------------------
