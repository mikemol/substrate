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
-- 1. The CoverData record.
--
-- A Cover X represents "a family of morphisms into X" that collectively
-- covers X. The substrate-honest encoding: each cover-witness produces
-- (Idx, source : Idx → Obj, family : (i : Idx) → Hom (source i) X)
-- via the CoverData record.
--
-- ⟡set1-paydown: the site is over a LARGE category (Obj : Set₁, Hom /
-- Cover Set-valued families), and CoverData carried a flat carrier
-- `Idx : Set` field — the whole `Category.Site` module sat at Set₂/Set₃.
-- Eliminate: every Set-valued field/carrier — Obj, Hom, the flat carrier
-- Idx AND its `source` — moves to a parameter, so CoverData holds only the
-- `family` field and lands in Set. Consumers write
-- `CoverData Obj Hom Idx source X`.
------------------------------------------------------------------------

record CoverData
  (Obj    : Set) (Hom : Obj → Obj → Set)
  (Idx    : Set) (source : Idx → Obj)
  (X      : Obj) : Set where
  field
    family : (i : Idx) → Hom (source i) X

open CoverData public

------------------------------------------------------------------------
-- 2. The Site record.
--
-- Parametric in:
--   * Obj : a type of objects
--   * Hom : Obj → Obj → Set, morphisms
--   * Cover : Obj → Set, the type of covers at each object
--   * Idx / source : the per-cover index family (source of the covering
--     morphisms) — the heterogeneous `Idx : Set` existential inside
--     CoverData, DEMATERIALIZED into an indexed family so the site is
--     honest about each cover choosing its own index set.
--
-- ⟡set1-paydown: Obj (was Set₁), Hom / Cover (Set-valued families), the
-- per-cover Idx/source family, AND the three Set-valued coverage-axiom
-- signature carriers (stability/transitivity/identity-stated : Set — a field
-- of type Set is itself a Set₁ source) are ALL module parameters; the record
-- holds only the cover-data realiser, so Site : Set. The heterogeneous
-- cover-data existential (each cover has its OWN Idx) is carried by the
-- `Idx : {X} → Cover X → Set` index family.
--
-- Coverage axioms (signature-bearing; concrete instances discharge them):
--   stability-stated    : pullback of a cover is a cover
--   transitivity-stated : cover-of-covers is a cover
--   identity-stated     : the singleton {id_X} is a cover
------------------------------------------------------------------------

record Site
  (Obj    : Set)
  (Hom    : Obj → Obj → Set)
  (Cover  : Obj → Set)
  (Idx    : {X : Obj} → Cover X → Set)
  (source : {X : Obj} (c : Cover X) → Idx c → Obj)
  (stability-stated transitivity-stated identity-stated : Set)
  : Set where
  field
    -- Each Cover X is realised by CoverData (per-cover Idx/source).
    cover-data : {X : Obj} (c : Cover X) →
                 CoverData Obj Hom (Idx c) (source c) X

open Site public

------------------------------------------------------------------------
-- 3. Capstone for UP11.
--
-- Site record landed. UP12 specialises to UPCategory: the canonical
-- coverage on UPCategory is "refinement families that exhaust the
-- target UP."
------------------------------------------------------------------------
