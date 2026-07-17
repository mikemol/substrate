------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Omega
--
-- UP32 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The subobject classifier Ω in PSh(UPCategory) / Sh(UPSite):
--
--   Ω(U) = "the set of sieves on U"
--
-- This is the canonical Grothendieck-topos Ω. Substrate-native: a
-- sieve at U is the Sieve record (UP13); Ω(U) is the family of all
-- such sieves.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Omega where

open import Substrate.Foundation.Product using (Σ)
open import Substrate.Category.UniversalProperty.Term using (UPTerm)
open import Substrate.Category.UniversalProperty.Sieve using (Sieve)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- 1. Ω as a presheaf-like function on objects.
  --
  -- ⟡ta-upterm-L5-reflow: objects are the Set₀ alphabet O; Sieve now lives
  -- at Set₁ (its `member` predicate lowered Set₁ → Set), so Ω lowers
  -- Set₂ → Set₁. (O, Hom) via the enclosing section.
  --
  -- ⟡rc-parameterize (⟡rerank2-floor-dissolve): the member predicate is A
  -- fiber family, not THE — so it is a PARAMETER of Ω, not an existential.
  -- Ω at a given member predicate is just the sieve carrying it, at Set₀.
  -- ("Ω is Set₁" was the wall-reflex; parameterize the family.)
  ------------------------------------------------------------------------

  Ω : (U : O) (member : {V : O} → UPTerm O Hom V U → Set) → Set
  Ω U member = Sieve O Hom U member

------------------------------------------------------------------------
-- 2. Capstone for UP32.
--
-- Subobject classifier signature lands. UP33 supplies the truth
-- value interpretation; UP34 internal logic.
------------------------------------------------------------------------
