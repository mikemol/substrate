------------------------------------------------------------------------
-- Substrate.Category.HC.InfCapstone
--
-- HC40 — ∞-categorical sub-arc capstone (HC31-HC40) + FULL HC-arc
-- + 80-SLICE SPRINT CLOSURE.
--
-- ===================================================================
-- 80-SLICE SPRINT FULL CLOSURE
-- ===================================================================
--
-- UP-arc (UP1-UP40) : UPCategory + Grothendieck topos of UPs.
--   Phase 1 : UPArrow + UPMorphism + UPTerm + ArrowOfArrow + FixedPoint
--             + UPCategory + Instances + Terminal
--   Phase 2 : Site + UPCover + Sieve + Pretopology + axioms
--             + ConcreteCovers + Refinement + Saturation
--   Phase 3 : UPPresheaf + Yoneda + UPSheaf + MatchingFamily
--             + Sheafify + ConstantSheaf + Pullback + InternalHom
--   Phase 4 : UPTopos + Ω + TruthValues + InternalLogic
--             + Powerset + GeometricMorphism + AdjointPair
--             + Substrate-UPTopos + HigherCatAsInternal
--
-- HC-arc (HC1-HC40) : 40 distinguished UPArrow objects in UPCategory.
--   Coherence sub-arc (HC1-HC10)
--   Braided / Symmetric sub-arc (HC11-HC20)
--   Double / Fibered sub-arc (HC21-HC30)
--   ∞-categorical sub-arc (HC31-HC40)
--
-- ===================================================================
-- STRUCTURAL CLOSURE
-- ===================================================================
--
-- The substrate's category-of-universal-properties IS a named topos.
-- Every higher-categorical concept (pentagon, hexagon, braided,
-- symmetric, Drinfeld center, double cat, fibered cat, simplicial
-- set, quasi-category, ∞-Yoneda, model category, Quillen adj,
-- ∞-limit) IS a named UPArrow object in the topos.
--
-- The user's "favourite category" — the fixed-point object in the
-- category of arrow categories — is the substrate's UPCategory
-- exhibited at UP5 (UPArrow²) + UP6 (ι and promote). The
-- tetrative-metacircularity now has a typed home.
--
-- Future arcs add UPs by inhabiting the UPCategory; coherence
-- diagrams become internal-logic equations; sheaf cohomology
-- of UPCategory becomes the substrate's structural cohomology
-- typed natively.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.HC.InfCapstone where

-- ∞-categorical sub-arc re-exports
open import Substrate.Category.HC.SimplicialSet      public using (SimplicialSet-UP)
open import Substrate.Category.HC.DeltaCategory      public using (DeltaCategory-UP)
open import Substrate.Category.HC.HornInclusion      public using (HornInclusion-UP)
open import Substrate.Category.HC.QuasiCategory      public using (QuasiCategory-UP)
open import Substrate.Category.HC.InfYoneda          public using (InfYoneda-UP)
open import Substrate.Category.HC.InfAdjunction      public using (InfAdjunction-UP)
open import Substrate.Category.HC.ModelCategory      public using (ModelCategory-UP)
open import Substrate.Category.HC.QuillenAdjunction  public using (QuillenAdjunction-UP)
open import Substrate.Category.HC.InfLimit           public using (InfLimit-UP)

-- Full HC-arc re-exports
open import Substrate.Category.HC.CoherenceCapstone     public
open import Substrate.Category.HC.BraidedSymCapstone    public
open import Substrate.Category.HC.DoubleFiberedCapstone public

-- UP-arc re-export
open import Substrate.Category.UniversalProperty.Capstone public
