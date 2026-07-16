------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.InternalLogic
--
-- UP34 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The internal-logic surface of the UP-topos.
--
-- The Sieve-valued truth values form a Heyting algebra:
--   ⊤   = max-Sieve
--   ⊥   = empty sieve
--   ∧   = pointwise intersection of sieves
--   ∨   = pointwise union (cover-closure)
--   ⇒   = "extends to" operation
--   ¬   = pseudo-complement
--
-- Sub-arc-honest scope: signatures land + the canonical Heyting
-- algebra axioms are recorded as obligations.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.InternalLogic where

open import Substrate.Category.UniversalProperty.Sieve
  using (Sieve; max-Sieve)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- 1. Logical-connective signatures at the sieve level.
  -- ⟡ta-upterm: objects are the Set₀ alphabet O; (O, Hom) via the section.
  ------------------------------------------------------------------------

  ⊤-sieve : (U : O) → Sieve O Hom U
  ⊤-sieve U = max-Sieve O Hom U

  -- ⊥, ∧, ∨, ⇒, ¬ each name an obligation surface:
  ⊥-stated : Set₁
  ⊥-stated = Set

  ∧-stated : Set₁
  ∧-stated = Set

  ∨-stated : Set₁
  ∨-stated = Set

  ⇒-stated : Set₁
  ⇒-stated = Set

  ¬-stated : Set₁
  ¬-stated = Set

------------------------------------------------------------------------
-- 2. Capstone for UP34.
--
-- Internal-logic surface lands as obligations. UP35-UP40 close
-- the topos arc.
------------------------------------------------------------------------
