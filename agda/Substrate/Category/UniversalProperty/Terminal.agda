------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Terminal
--
-- UP9 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The terminal object in UPCategory is subtle because UPMorphism's
-- target-map is CONTRAVARIANT — for a "trivial" UP with Target = ⊤
-- to be terminal we would need ⊤ → Target U for every U, which
-- requires a chosen point of Target U.
--
-- Substrate-honest scope:
--   * trivial-UP IS terminal CONDITIONAL on a target-base witness.
--   * The unique morphism to trivial-UP exists for UPs equipped
--     with a designated Target inhabitant.
--   * The unconditional terminal in Arr(Span) is the OPPOSITE
--     direction: trivial-UP with Source = ⊥ is INITIAL on the
--     source side, which becomes terminal in the
--     contravariant-target reading.
--
-- This slice records the conditional terminal + sketches the
-- UPCategory → Cat embedding.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Terminal where

open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Category.UniversalProperty
  using (UPArrowP; SourceP; TargetP; WitnessP; trivial-UPP)
open import Substrate.Category.UniversalProperty.Morphism
  using (UPMorphism)

-- ⟡UPArrow-dissolve C: telescope carriers (auto).
private variable
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
