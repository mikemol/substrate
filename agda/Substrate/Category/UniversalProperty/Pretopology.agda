------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Pretopology
--
-- UP15 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- A Grothendieck pretopology on UPCategory: an assignment to each
-- UPArrow U of a set of UPCovers (the "designated covers") closed
-- under stability + transitivity + identity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Pretopology where

open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.UniversalProperty.Coverage using (UPCover)

------------------------------------------------------------------------
-- 1. Pretopology record.
------------------------------------------------------------------------

record UPPretopology : Set₃ where
  field
    designated : (U : UPArrow) → UPCover U → Set
    -- The three Grothendieck axioms, signature-bearing.
    identity-axiom-stated     : Set
    stability-axiom-stated    : Set
    transitivity-axiom-stated : Set

------------------------------------------------------------------------
-- 2. Capstone for UP15.
--
-- UP16 supplies the axiom statements explicitly; UP17 the discrete
-- pretopology (everything is a cover); UP18-UP20 saturation +
-- concrete instances + capstone.
------------------------------------------------------------------------
