------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.HigherCatAsInternal
--
-- UP39 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Higher-categorical content as internal objects of the
-- Substrate-UPTopos.
--
-- Every higher-categorical concept — pentagon coherence, braided
-- monoidal structure, double categories, ∞-categorical Kan
-- fillings — is internal data of the UP-Topos:
--
--   * A monoidal-structure-UP is a UPArrow whose Source is "a
--     category" and whose Target is "a monoidal structure on it,"
--     with the Witness encoding the coherence diagrams.
--   * A braided-monoidal-structure-UP is a UPArrow refining the
--     monoidal-structure-UP via an extra braiding-with-hexagon.
--   * A double-category-structure-UP refines a 2-cat-UP with
--     square composition.
--   * An ∞-category-structure-UP carries Kan-fill obligations.
--
-- The HC-arc (HC1-HC40) discharges concrete UP-instances for each
-- of these. UP39 names the SHAPE of "higher-cat as internal."
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.HigherCatAsInternal where

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)

------------------------------------------------------------------------
-- 1. The "higher-categorical-structure" UP shape.
--
-- Substrate-honest signature: each higher-cat concept's UP
-- inhabits this shape. HC-arc supplies them.
------------------------------------------------------------------------

HC-Structure-Shape : Set₁
HC-Structure-Shape = UPArrow

-- Concrete instances (HC1-HC40):
--   Coherence-UP, Pentagon-UP, Braided-UP, Symmetric-UP,
--   Cartesian-UP, Double-UP, Fibered-UP, Simplicial-UP,
--   Quasi-Category-UP, Kan-Complex-UP, ModelCategory-UP

-- Each is a UPArrow + UPGen + ... + (UPTerm into the Coherence-UP
-- giving its specific obligations).

------------------------------------------------------------------------
-- 2. Capstone for UP39.
--
-- The shape lands. UP40 closes the UP-arc; HC1-HC40 supply the
-- concrete higher-cat content.
------------------------------------------------------------------------
