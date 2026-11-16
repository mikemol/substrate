------------------------------------------------------------------------
-- Substrate.Category.Allegory.Policy.SplitDedupe
--
-- Defines: SplitDedupe
--
-- THE CONSERVATION POLICY AND THE GRANULARITY POLICY ARE ONE MEET.
--
--   A  "We never erase a lemma or proof.  We only deduplicate."
--   B  "It doesn't matter if nothing is importing it, I still want it split."
--
-- ⚑ I OFFERED THESE AS TWO READINGS AND ASKED WHICH ONE HELD.  The
-- operator's reply — "A and B are not incompatible" — was the correction,
-- and it is the construct-dont-classify failure exactly: I built an
-- either/or and asked for a pick, where the move was to construct the
-- structure both are readings of.  They are the two DIRECTIONS of one
-- thing.  Split refines (one file of n definitions becomes n files of
-- one); dedupe collapses, and only along a proved equality.  A bounds
-- collapse; B bounds refinement.  Neither is reachable without the other,
-- which is why they could not have been incompatible.
--
-- ⚑ AND `_∧_` IS CHARACTERISED AS A GLB HERE, NOT EQUATIONALLY — which is
-- what makes this the right term rather than a convenient one.
-- Allegory.agda proves `∧-⊆ˡ`, `∧-⊆ʳ`, `∧-greatest`: the largest thing
-- below both.  It does NOT prove idempotence, commutativity or
-- associativity (searched `∧-idem`, `∧-comm`, `∧-assoc` — no definers).
-- The terminal state of the corpus is the GREATEST corpus satisfying both
-- constraints, so the universal property IS the policy statement and the
-- missing equational laws are not needed.
--
-- ⚑ CONSUMER COUNT IS NOT THE CRITERION, and the operator said so
-- directly.  Consumer count is a fact about the IMPORT GRAPH; the target
-- is a property of the DEFINITION SET.  Reaching for the import graph is
-- the same error as reading a build log's `Checking` lines as progress —
-- measuring the easy thing rather than the meant thing.
--
-- ⟡policy-allegory: one lemma, one elaboration unit; no barrel
-- re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Policy.SplitDedupe where

open import Substrate.Category.Allegory
open import Substrate.Category.Allegory.Policy.Corpus


-- `refined` relates a corpus state to the states reachable by splitting;
-- `conserved` to those reachable by a collapse that erased nothing.  The
-- admissible moves are their meet — and by `∧-greatest` this is the
-- LARGEST such relation, so nothing admissible is excluded by fiat.
SplitDedupe : {Site : Set} → Corpus Site
            → (Site → Site → Set) → (Site → Site → Set) → Site → Site → Set
SplitDedupe _ refined conserved = refined ∧ conserved
