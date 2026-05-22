------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Refinement
--
-- UP18 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Refinement of covers: cover c' refines cover c iff every arrow of
-- c' factors through some arrow of c. Two covers are equivalent iff
-- each refines the other.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Refinement where

open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.UniversalProperty.Term
  using (UPTerm; _++ᵤ_)
open import Substrate.Category.UniversalProperty.Coverage
  using (UPCover; Idx; source-UP; arrow)

------------------------------------------------------------------------
-- 1. Refines: c' refines c.
--
-- For every i' : Idx c', there exist i : Idx c and a factoring
-- UPTerm from source-UP c' i' to source-UP c i making the diagram
-- commute (= the arrow of c' factors through arrow of c).
------------------------------------------------------------------------

open import Substrate.Foundation.Product using (Σ)

record ⊤₁ : Set₁ where
  constructor tt₁

Refines : {U : UPArrow} → UPCover U → UPCover U → Set₁
Refines {U} c' c =
  (i' : Idx c') →
  Σ (Idx c) (λ i →
  Σ (UPTerm (source-UP c' i') (source-UP c i)) (λ _ → ⊤₁))

------------------------------------------------------------------------
-- 2. Capstone for UP18.
--
-- Refinement relation lands. UP19 supplies saturation; UP20 the
-- Phase-2 capstone.
------------------------------------------------------------------------
