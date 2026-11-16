------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Terminal.ToTrivialCond
--
-- Defines: to-trivial-cond
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.Terminal; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Terminal.ToTrivialCond where

open import Substrate.Foundation.Unit
open import Substrate.Category.UniversalProperty
open import Substrate.Category.UniversalProperty.Morphism
variable
  SU TU : Set
  WU : SU → TU → Set



------------------------------------------------------------------------
-- 1. Conditional terminal morphism.
--
-- For a UPArrow U equipped with a target-base, supply the unique
-- morphism U → trivial-UP.
------------------------------------------------------------------------

to-trivial-cond :
  (U : UPArrowP SU TU WU) →
  (target-base : TargetP U) →
  (universal-witness : (s : SourceP U) → WitnessP U s target-base) →
  UPMorphism U trivial-UPP
to-trivial-cond U target-base universal-witness = record
  { source-map = λ _ → tt
  ; target-map = λ _ → target-base
  ; coherent   = λ s _ _ → universal-witness s
  }

------------------------------------------------------------------------
-- 2. The substrate-honest reading.
--
-- UPCategory is naturally enriched with the CHOICE of target-base
-- at every object. Under that enrichment, trivial-UP is terminal
-- unconditionally. Without the enrichment, UPCategory has a
-- conditional terminal that fires per-object.
--
-- The substrate's [[choice-rigidification]] discipline applies:
-- declaring trivial-UP as "THE terminal" would rigidify the
-- target-base choice. The conditional form preserves gauge.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 3. UPCategory → Cat embedding (sketch).
--
-- The map sending a UPArrow U to a category Solve(U) and a UPTerm
-- t : U → V to a functor Solve(V) → Solve(U) lands as a
-- contravariant functor UPCategory → Cat. The construction:
--
--   Solve(U) :
--     objects   = pairs (s : Source U, i : Target U) with Witness U s i
--     morphisms = (s, i) → (s', i') such that source-map / target-map
--                 preserve the witness
--
-- Full functoriality is mechanical from UPMorphism composition; the
-- bridge construction is recorded as a UP20+ slice obligation.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 4. Capstone for UP9.
--
-- Conditional terminal landed. UP10 supplies Phase-1 capstone.
------------------------------------------------------------------------
