------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Phase1
--
-- UP10 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Phase-1 capstone: UPCategory foundations landed.
--
-- ===================================================================
-- PHASE-1 SUMMARY (UP1-UP10)
-- ===================================================================
--
--   UP1   UniversalProperty.agda            UPArrow = Arr(Span) object
--   UP2   UniversalProperty/Morphism.agda   UPMorphism = square in Arr(Span)
--   UP3   UniversalProperty/Compose.agda    id + composition (records)
--   UP4   UniversalProperty/Term.agda       UPGen + UPTerm = term algebra
--   UP5   UniversalProperty/ArrowOfArrow    L2 meta-arrow (arrow-of-arrows)
--   UP6   UniversalProperty/FixedPoint      ι + promote: fixed-point pair
--   UP7   UniversalProperty/Category.agda   UPCategory record + laws
--   UP8   UniversalProperty/Instances.agda  5 canonical UPArrow instances
--   UP9   UniversalProperty/Terminal.agda   conditional terminal + Cat sketch
--   UP10  Phase1.agda                       this file
--
-- ===================================================================
-- STRUCTURAL CLOSURE
-- ===================================================================
--
-- The substrate's universal-property catalogue is now organised as
-- an object of Arr(Span), with morphisms living as a term algebra
-- (UPTerm = typed cons-list of UPGen) instead of opaque records.
-- The category laws hold STRUCTURALLY at the term level (refl /
-- one-step induction).
--
-- The user's "favourite category" — the fixed-point object in the
-- category of arrow categories — is exhibited explicitly:
--
--   * UPArrow IS an arrow object in Arr(Span) by record shape.
--   * UPMorphism IS a commuting square (the morphism shape in
--     Arr(Span)).
--   * UPArrow² (UP5) names the meta-level arrow-of-arrows.
--   * ι : UPArrow² → UPArrow (UP6) and promote : UPArrow → UPArrow²
--     (UP6) exhibit the fixed-point pair.
--
-- The tetrative-metacircularity memory entry now has a SLICE
-- WITNESS: the substrate's structural reflection at L2 IS named
-- and embedded back into L0 via ι.
--
-- ===================================================================
-- NEXT PHASES
-- ===================================================================
--
--   Phase 2 (UP11-UP20) : Site structure on UPCategory.
--   Phase 3 (UP21-UP30) : Presheaves + sheaves.
--   Phase 4 (UP31-UP40) : Grothendieck topos.
--   HC arc (HC1-HC40)   : Higher-cat content as internal objects.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Phase1 where

open import Substrate.Category.UniversalProperty            public
  using (UPArrow; Source; Target; Witness; trivial-UP;
         UniversalProperty; Spec; Inst; solves)
open import Substrate.Category.UniversalProperty.Morphism   public
  using (UPMorphism; source-map; target-map; coherent)
open import Substrate.Category.UniversalProperty.Compose    public
  using (id-UPMorphism; compose-UPMorphism)
open import Substrate.Category.UniversalProperty.Term       public
  using (UPGen; lift; UPTerm; []; _∷_; _++ᵤ_)
open import Substrate.Category.UniversalProperty.ArrowOfArrow public
  using (UPArrow²; L0-Source; L0-Target; L1-Witness; UPArrow²-Morphism)
open import Substrate.Category.UniversalProperty.FixedPoint public
  using (ι; promote)
open import Substrate.Category.UniversalProperty.Category   public
  using (UPCategory; UPCategory-canonical;
         id-UPTerm; compose-UPTerm; ++ᵤ-identityˡ;
         ++ᵤ-identityʳ; ++ᵤ-assoc)
open import Substrate.Category.UniversalProperty.Instances  public
  using (FreeMonoid-UP; FreeModule-UP; ConeLimit-UP;
         Adjunction-UP; FreeLinearization-UP)
open import Substrate.Category.UniversalProperty.Terminal   public
  using (to-trivial-cond)

------------------------------------------------------------------------
-- UPCategory Phase-1 closure: ready for Phase 2's site structure.
------------------------------------------------------------------------
