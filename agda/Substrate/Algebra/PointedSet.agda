------------------------------------------------------------------------
-- Substrate.Algebra.PointedSet
--
-- F1m1 of the F₁-modules-as-pointed-sets arc per
-- [scratch/m_mod_arc_plan.md] (sibling towers section).
--
-- A PointedSet is a Set A equipped with a distinguished element
-- `base : A`. This is the substrate-native carrier for the F₁
-- semantics: F₁-modules ARE pointed sets, and GL(n, F₁) = Sₙ
-- (permutations of the basepoint-distinct elements).
--
-- Per [[feedback-categorical-name-first]]: "pointed set" is the
-- categorical name for what F₁-Module means; PointedSet is its
-- record form.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PointedSet where

open import Substrate.Foundation.Unit using (⊤; tt)

------------------------------------------------------------------------
-- 1. The PointedSet record.
------------------------------------------------------------------------

record PointedSet : Set₁ where
  field
    Carrier : Set
    base    : Carrier

open PointedSet public

------------------------------------------------------------------------
-- 2. The trivial PointedSet: ⊤ with its unique element.
--
-- This is F₁ itself viewed as a pointed set (no non-trivial
-- elements beyond the basepoint).
------------------------------------------------------------------------

⊤-Pointed : PointedSet
⊤-Pointed = record { Carrier = ⊤ ; base = tt }

------------------------------------------------------------------------
-- 3. Capstone for F1m1.
--
-- PointedSet landed. F1m2 supplies PointedSetMap (basepoint-
-- preserving function); F1m3 identifies F₁-Module = PointedSet;
-- F1m4 builds GL(n, F₁) = Sₙ.
------------------------------------------------------------------------
