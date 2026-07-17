------------------------------------------------------------------------
-- Σ-SEAM-GLUE / Ω2-instance — the M40 closure ON the categorical spine.
--
-- ΞB2ii grounded A4Z2 as an Algebra.Group; the categorical-grounding advisory
-- flagged Algebra.* as PARALLEL to Category.* ("fix once at the hierarchy
-- level"). Category.DeloopingGroup is that fix (Group → groupoid). This module
-- applies it to A4Z2-Group: the realized M40 closure A₄×ℤ₂ is now a substrate
-- `CategoryOf` (its one-object delooping) AND a groupoid (every morphism
-- invertible), so M40 sits ON the categorical spine, not just in Algebra.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.M40Groupoid where

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Algebra.Group using (monoid)
open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Delooping using (deloop)
open import Substrate.Category.DeloopingGroup using (IsGroupoid; deloop-group-isGroupoid)
open import Substrate.WitnessTower.M40Closure using (A4Z2)
open import Substrate.WitnessTower.M40Group using (A4Z2-Group)

-- A₄×ℤ₂ as a one-object category (the delooping of its group) — on the spine.
A4Z2-CategoryOf : CategoryOf ⊤ (λ _ _ → A4Z2)
A4Z2-CategoryOf = deloop (monoid A4Z2-Group)

-- ... and it is a GROUPOID: every morphism (every group element) is invertible.
A4Z2-isGroupoid : IsGroupoid A4Z2-CategoryOf
A4Z2-isGroupoid = deloop-group-isGroupoid A4Z2-Group
