------------------------------------------------------------------------
-- Substrate.Category.Site
--
-- UP11 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The generic Site record: a category C equipped with a "coverage"
-- assigning each object X a family of "covers" — sets of morphisms
-- into X that collectively determine X.
--
-- Substrate-native scope: signature-bearing. The full coverage
-- axioms (stability under pullback, transitivity) are obligation
-- fields. Concrete instances (UPSite at UP18) populate them.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Site where

------------------------------------------------------------------------
-- 1. The Site record.
--
-- Parametric in:
--   * Obj : a type of objects
--   * Hom : Obj → Obj → Set, morphisms
--   * Cover : Obj → Set, the type of covers at each object
--
-- A Cover X represents "a family of morphisms into X" that collectively
-- covers X. The substrate-honest encoding: each cover-witness produces
-- (Idx, source : Idx → Obj, family : (i : Idx) → Hom (source i) X)
-- via the CoverData record.
------------------------------------------------------------------------

record CoverData
  (Obj : Set₁) (Hom : Obj → Obj → Set₁)
  (X : Obj) : Set₂ where
  field
    Idx    : Set
    source : Idx → Obj
    family : (i : Idx) → Hom (source i) X

open CoverData public

record Site : Set₃ where
  field
    Obj   : Set₁
    Hom   : Obj → Obj → Set₁
    Cover : Obj → Set₂
    -- Each Cover X is realised by CoverData
    cover-data : {X : Obj} → Cover X → CoverData Obj Hom X
    -- Coverage axioms (signature-bearing; concrete instances
    -- discharge them):
    --   stability : pullback of a cover is a cover
    --   transitivity : cover-of-covers is a cover
    --   identity : the singleton {id_X} is a cover
    stability-stated    : Set
    transitivity-stated : Set
    identity-stated     : Set

open Site public

------------------------------------------------------------------------
-- 2. Capstone for UP11.
--
-- Site record landed. UP12 specialises to UPCategory: the canonical
-- coverage on UPCategory is "refinement families that exhaust the
-- target UP."
------------------------------------------------------------------------
