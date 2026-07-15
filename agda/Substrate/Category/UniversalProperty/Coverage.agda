------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Coverage
--
-- UP12 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Coverage on UPCategory: a family of UPTerms into a UPArrow U is a
-- COVER of U if the source UPs collectively exhaust the structural
-- content of U.
--
-- The canonical "exhausting" relation for the substrate: the
-- family's source-maps cover Source U, and the family's target-maps
-- cover Target U. This is the standard Grothendieck-coverage move
-- specialised to Arr(Span).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Coverage where

open import Substrate.Category.UniversalProperty
  using (UPArrowP; mkUP; SourceP; TargetP)
open import Substrate.Category.UniversalProperty.Term
  using (UPTerm)

-- ⟡UPArrow-dissolve C: telescope carriers (auto).
private variable
  SU TU : Set
  WU : SU → TU → Set

------------------------------------------------------------------------
-- 1. UPCover: an indexed family of UPTerms into U.
--
-- A cover at U is a small-set-indexed family { Vᵢ → U }ᵢ where each
-- Vᵢ → U is a UPTerm.
------------------------------------------------------------------------

-- ⟡UPArrow-dissolve C: the source objects are a family with per-index carriers,
-- so the object-assignment is CARRIER-FAMILIES (Sc/Tc/Wc : Idx → Set), NOT a stored
-- Σ-bundle — the source at i is the trivial `mkUP {Sc i}{Tc i}{Wc i}`. `source-UP` is
-- the shim reading it back. UPCover : Set₁ (from the UPTerm field), no bundle def.
record UPCover (U : UPArrowP SU TU WU) : Set₁ where
  field
    Idx   : Set
    Sc Tc : Idx → Set
    Wc    : (i : Idx) → Sc i → Tc i → Set
    arrow : (i : Idx) → UPTerm (mkUP {Sc i} {Tc i} {Wc i}) U

open UPCover public

source-UP : {U : UPArrowP SU TU WU} (c : UPCover U) (i : Idx c)
          → UPArrowP (Sc c i) (Tc c i) (Wc c i)
source-UP _ _ = mkUP

------------------------------------------------------------------------
-- 2. The covering condition (signature).
--
-- A cover { Vᵢ → U } collectively-exhausts U if every (s, i) in
-- Source U × Target U with Witness U s i factors through some Vᵢ.
-- Substrate-honest: the condition is named as an obligation Set;
-- concrete covers (UP17) discharge it.
------------------------------------------------------------------------

Covering : {U : UPArrowP SU TU WU} → UPCover U → Set₁
Covering _ = Set  -- obligation placeholder

------------------------------------------------------------------------
-- 3. Capstone for UP12.
--
-- UPCover shape lands; the covering condition is named. UP13 supplies
-- sieves; UP14-UP16 the coverage axioms (stability, transitivity);
-- UP17-UP20 concrete instances + saturation.
------------------------------------------------------------------------
