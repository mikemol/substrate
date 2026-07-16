------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Refinement
--
-- UP18 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Refinement of covers: cover c' refines cover c iff every arrow of
-- c' factors through some arrow of c. Two covers are equivalent iff
-- each refines the other.
--
-- ⟡ta-upterm: objects are the Set₀ alphabet O; homs are UPTermO O Hom.
-- The factoring term lowers Set₁ → Set (UPTermO is Set₀), so Refines
-- lowers Set₁ → Set; the bespoke `⊤₁ : Set₁` is replaced by the Set₀ `⊤`.
-- (O, Hom) via the enclosing section.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Refinement where

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Foundation.Product using (Σ)
open import Substrate.Category.UniversalProperty.Term using (UPTermO)
open import Substrate.Category.UniversalProperty.Coverage
  using (UPCover; Idx; source-UP)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- 1. Refines: c' refines c.
  --
  -- For every i' : Idx c', there exist i : Idx c and a factoring
  -- UPTermO from source-UP c' i' to source-UP c i making the diagram
  -- commute (= the arrow of c' factors through arrow of c).
  ------------------------------------------------------------------------

  Refines : {U : O} → UPCover O Hom U → UPCover O Hom U → Set
  Refines {U} c' c =
    (i' : Idx c') →
    Σ (Idx c) (λ i →
    Σ (UPTermO O Hom (source-UP O Hom c' i') (source-UP O Hom c i)) (λ _ → ⊤))

------------------------------------------------------------------------
-- 2. Capstone for UP18.
--
-- Refinement relation lands. UP19 supplies saturation; UP20 the
-- Phase-2 capstone.
------------------------------------------------------------------------
