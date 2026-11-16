------------------------------------------------------------------------
-- Substrate.Category.Allegory.Policy.UnnamedUse
--
-- Defines: unnamed-use-unmeasurable
--
-- ⚑ THE TERM THAT SAYS WHY THE BASIS SHIFT IS PARTIAL, and it is a
-- REFUTATION rather than a policy.  NameIdentity is `use ⊆ def`: every
-- name arriving at a use site is implied by the definition site.  That
-- statement quantifies over NAMES.  `getattr(o, s)` — 113 sites measured
-- across this repo's python — writes no name: the name is a VALUE
-- computed at runtime.
--
-- So the python `use` relation is not a relation on the same carrier.
-- Formalized: if the name a site uses is drawn from an EMPTY name type,
-- `use ⊆ def` holds VACUOUSLY — for every relation `def` whatsoever,
-- including one that carries nothing at all.  A policy satisfied by every
-- definition set is not being satisfied; it has no subject.
--
-- ⚑⚑ AND THAT IS THE PRECISE SENSE IN WHICH THIS IS NOT `state ∖ budget`.
-- Owed measures offenders against a budget inside a state space; a
-- vacuous inclusion is not an offender the ratchet forgives, it is one
-- the ratchet cannot see.  `census-green-is-a-fact-about-the-census`
-- made a type: the green here reports the boundary of what the
-- instrument can express, and reading it as compliance is the error the
-- term exists to block.
--
-- ⚑ WHAT WOULD CLOSE IT — stated so this reads as WORK, not a wall.  The
-- repair is not a stronger policy but a RICHER Name type: one whose
-- inhabitants include runtime-constructed names, at which point `use ⊆
-- def` becomes contentful again and `getattr` sites are measurable
-- offenders rather than unmeasurable ones.  That is a real construction
-- (the name would carry its provenance), not a reformulation — and it is
-- the same move as the Tarski universe, where "the category of all Sets"
-- stops being a floor once the universe is REPRESENTED generatively
-- rather than held.
--
-- ⟡policy-basis-shift: one lemma, one elaboration unit; no barrel
-- re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Policy.UnnamedUse where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Category.Allegory
open import Substrate.Category.Allegory.Policy.Corpus
open import Substrate.Category.Allegory.Policy.NameIdentity


-- With no writable names, name-identity holds against ANY definition
-- relation — including the empty one.  The proof is absurd-elimination on
-- the name: there is no name at which to test the inclusion.
--
-- Read as a measurement: this is the verdict a name-identity census
-- returns over the 113 `getattr` sites, and it is green for a reason that
-- has nothing to do with those sites complying.
unnamed-use-unmeasurable :
    {Site : Set} (c : Corpus Site)
  → (use def : Site → ⊥ → Set)
  → NameIdentity c use def
unnamed-use-unmeasurable _ _ _ _ ()
