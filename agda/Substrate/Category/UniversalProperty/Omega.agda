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
  -- ⟡rc-topos (⟡set1-rerank2): Sieve's `member` predicate is now a PARAMETER,
  -- not a field — Ω(U) genuinely quantifies over "which member predicate",
  -- so the honest Set₁ shape is a Σ: the member predicate paired with a
  -- sieve carrying it. This Σ-holder is the documented Set₁ residue (this
  -- is the only def in the file that needs it).
  ------------------------------------------------------------------------

  Ω : O → Set₁
  Ω U = Σ ({V : O} → UPTerm O Hom V U → Set) (λ m → Sieve O Hom U m)

------------------------------------------------------------------------
-- 2. Capstone for UP32.
--
-- Subobject classifier signature lands. UP33 supplies the truth
-- value interpretation; UP34 internal logic.
------------------------------------------------------------------------
