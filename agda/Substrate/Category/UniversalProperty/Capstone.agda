------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Capstone
--
-- UP40 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- UP-ARC FULL CAPSTONE.
--
-- ===================================================================
-- UP-ARC CLOSURE (UP1-UP40)
-- ===================================================================
--
-- Phase 1 (UP1-UP10): UPCategory foundations.
--   UPArrow ⊆ Obj(Arr(Span))
--   UPMorphism = squares in Arr(Span)
--   UPTerm = substrate-native term algebra
--   UPArrow² + ι + promote = fixed-point pair
--   UPCategory record + structural category laws
--
-- Phase 2 (UP11-UP20): Site structure.
--   UPCover + Sieve + generated-Sieve
--   UPPretopology + identity/stability/transitivity axioms
--   Concrete covers + Refinement + Saturation
--
-- Phase 3 (UP21-UP30): Presheaves + sheaves.
--   UPPresheaf + Yoneda よ at Set₁
--   UPSheaf + MatchingFamily + Sheafify signature
--   Constant / Pullback / InternalHom signatures
--   Substrate's InstancesAt signature
--
-- Phase 4 (UP31-UP40): Grothendieck topos.
--   UPTopos + Ω + truth values + internal logic
--   Powerset / GeometricMorphism / AdjointPair signatures
--   Substrate-UPTopos lands as canonical named object
--   HigherCatAsInternal names the HC-arc target shape
--
-- ===================================================================
-- STRUCTURAL CLOSURE NARRATIVE
-- ===================================================================
--
-- The substrate's universal-property catalogue is now organised as
-- a NAMED TOPOS — the Grothendieck topos of sheaves on the
-- UP-site. Every existing UP record (FreeOverBasis, Limit, Cone,
-- Adjunction, FreeBasisUniversal, ...) is an OBJECT in
-- UPCategory; every refinement between them is a morphism;
-- every coherence diagram is an internal-logic statement.
--
-- The user's framing of "the category that is an object in the
-- category of arrow categories" is exhibited STRUCTURALLY:
--   * UPArrow IS an arrow object in Arr(Span).
--   * UPMorphism IS a square in Arr(Span).
--   * UPArrow² (UP5) names the L2 meta-arrow-of-arrows.
--   * ι : UPArrow² → UPArrow + promote : UPArrow → UPArrow² (UP6)
--     are the fixed-point pair.
--
-- The substrate's [[homology-cohomology-recursion]] memory has a
-- TYPED HOME: observed-UPs are presheaves, catalogued-UPs are
-- sheaves under descent, and the topos's internal logic is the
-- substrate's structural-consistency discipline made categorical.
--
-- HC-arc (HC1-HC40) will populate this topos with concrete higher-
-- categorical content as internal objects. Future arcs add new
-- UPs by INHABITING the UPCategory, not by adding scattered
-- record files.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Capstone where

-- Phase 1 re-exports
open import Substrate.Category.UniversalProperty.Phase1     public

-- Phase 2 re-exports
open import Substrate.Category.UniversalProperty.Phase2     public

-- Phase 3 re-exports
open import Substrate.Category.UniversalProperty.Phase3     public

-- Phase 4 final-set re-exports
open import Substrate.Category.UniversalProperty.Topos              public
  using (UPTopos)
open import Substrate.Category.UniversalProperty.Omega              public
  using (Ω)
open import Substrate.Category.UniversalProperty.TruthValues        public
  using (is-instance-truth)
open import Substrate.Category.UniversalProperty.InternalLogic      public
  using (⊤-sieve)
open import Substrate.Category.UniversalProperty.Powerset           public
  using (PowersetType)
open import Substrate.Category.UniversalProperty.GeometricMorphism  public
  using (GeometricMorphism)
open import Substrate.Category.UniversalProperty.AdjointPair        public
  using (SheafAdjointPair)
open import Substrate.Category.UniversalProperty.SubstrateTopos     public
  using (Substrate-UPTopos)
open import Substrate.Category.UniversalProperty.HigherCatAsInternal public
  using (HC-Structure-Shape)

------------------------------------------------------------------------
-- UP-arc closure: Substrate-UPTopos is the substrate's structural
-- cohomology made into a named topos. Ready for HC1-HC40 to populate.
------------------------------------------------------------------------
