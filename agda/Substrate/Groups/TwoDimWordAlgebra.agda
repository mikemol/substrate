------------------------------------------------------------------------
-- Substrate.Groups.TwoDimWordAlgebra
--
-- Capstone module for the substrate's 2-D word algebra construction.
--
-- The 2-D word algebra IS the DirectProduct of a "phase" Coxeter
-- group (capturing modular structure at order n) with a "cycle"
-- Coxeter group (capturing the orthogonal counting axis). The
-- substrate's existing Coxeter.DirectProduct combinator + the
-- FreeCyclic-Coxeter primitive (slice 1) are all that's needed to
-- construct it; no new primitives.
--
-- Per the user's framing: the 2-D structure catches the orthogonal
-- dimension the modular reading gives. The phase axis = the
-- quotient (Z/n); the cycle axis = the cover (ℕ via FreeCyclic).
-- Together they form the universal cover ℕ → Z/n.
--
-- This module re-exports the canonical instances + names the pattern.
-- No new content; everything has been built in slices 1-9 of the arc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.TwoDimWordAlgebra where

------------------------------------------------------------------------
-- The 2-D primitives.
------------------------------------------------------------------------

-- The FreeCyclic-Coxeter primitive (ℕ via word algebra, the "cycle"
-- axis).
import Substrate.Groups.FreeCyclic-Coxeter
import Substrate.Groups.FreeCyclic-Coxeter-Length

-- The 2-D direct product instances at Z₃, Z₄.
import Substrate.Groups.Z3-x-FreeCyclic
import Substrate.Groups.Z4-x-FreeCyclic
import Substrate.Groups.Z3-x-FreeCyclic-PhaseProjection
import Substrate.Groups.Z4-x-FreeCyclic-PhaseProjection

-- Operational correspondences.
import Substrate.Groups.Z-x-FreeCyclic-Recovery
import Substrate.Groups.Z-x-FreeCyclic-PhaseAdvance

------------------------------------------------------------------------
-- Capstone — 2-D word algebra arc complete.
--
-- The 10-slice arc:
--
--   #1 FreeCyclic-Coxeter         — ⟨a | (no relations)⟩, ℕ as monoid.
--   #2 FreeCyclic-Coxeter-Length  — bijection Word ↔ ℕ.
--   #3 Z3-x-FreeCyclic            — DirectProduct, n=3 instance.
--   #4 Z3-x-FreeCyclic-PhaseProj  — phase-project at n=3.
--   #5 Z4-x-FreeCyclic            — n=4 mirror.
--   #6 Z4-x-FreeCyclic-PhaseProj  — n=4 phase-project.
--   #7 Z-x-FreeCyclic-Recovery    — embed + phase-recovery, split cover.
--   #8 Z-x-FreeCyclic-PhaseAdvance — phase-advance ≡ σₙ via bijection.
--   #9 project_cycle_generator_as_2_cocycle memory.
--   #10 THIS capstone.
--
-- The substrate now has a substrate-native 2-D word algebra. Each
-- new Zₙ-x-FreeCyclic instance is one DirectProduct instantiation
-- + one ~30-line projection file. Mechanically extensible to any
-- n where the underlying Zₙ-Coxeter exists.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: the 2-D structure
-- IS our substrate-native answer to "how do you express cover
-- constructions / modular arithmetic without stdlib's Data.Nat.DivMod
-- or Data.Fin.Permutation."
--
-- Per [[project-cycle-generator-as-2-cocycle]]: the cycle generator
-- IS a 2-cocycle witness; the 2-D structure IS the cocycle-bookkeeping
-- device. Z/4 vs V₄ = the two H²(Z/2; Z/2) cohomology classes.
--
-- Per [[project-graded-bicategorical-arc]] (queued NEXT arc): the
-- 2-D structure with FreeCyclic as the grading axis gives strict
-- 2-monoid / graded bicategory structure for free. The substrate's
-- Coxeter framework already implicitly carries it; the next arc
-- names and surfaces it.
--
-- Deferred follow-ons (in addition to the queued graded arc):
--
--   * Cycle-incrementing phase-advance: currently the phase-advance
--     operation leaves cycle invariant. The "true" cover behavior
--     would increment cycle at the phase wraparound. This requires
--     conditional logic on canonical position, which the graded arc
--     will handle naturally.
--
--   * Z5-x-FreeCyclic and beyond: instances at higher n via the
--     same DirectProduct pattern. Trivially extensible.
--
--   * Non-trivial action (semidirect): FreeCyclic could act
--     non-trivially on Zₙ (e.g., phase-flip per cycle), giving
--     more interesting cover structures. Substrate has
--     SemidirectProductGroup for this; combining with FreeCyclic
--     opens dihedral / wreath-product instances.
--
--   * CRT-style decomposition: Z/(mn) at coprime m, n decomposes
--     as Z/m × Z/n. The 2-D word algebra DIRECT product naturally
--     expresses this when the components are coprime cyclic. Full
--     CRT primitive would automate Z/6 = Z/2 × Z/3, etc.
------------------------------------------------------------------------
