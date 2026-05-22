------------------------------------------------------------------------
-- Substrate.Groups.Manifest
--
-- Tier 1 cross-Zₙ feature-completeness check.
--
-- This module imports every existing (Zₙ × Capability) cell. If any
-- module is missing, broken, or renamed, this manifest fails to
-- typecheck — a build-discipline coverage signal.
--
-- The (M, N)-shape Cone, with M = ZnInstance, N = Capability:
--
--   capability \ n  | Z₂ | Z₃ | Z₄ | Z₅ | Z₇ |
--   ----------------|----|----|----|----|----|
--   Coxeter         | ✓  | ✓  | ✓  | ✓  | ✓  |
--   Coxeter-Group   | ✓  | ✓  | ✓  | ✓  | ·  |
--   Coxeter-S2M     | ·  | ✓  | ✓  | ✓  | ·  |
--   Coxeter-Fin     | ·  | ✓  | ✓  | ✓  | ·  |
--   x-FreeCyclic    | ·  | ✓  | ✓  | ✓  | ·  |
--   x-FC-PhaseProj  | ·  | ✓  | ✓  | ✓  | ·  |
--   x-FC-Degree     | ·  | ✓  | ·  | ·  | ·  |
--   x-FC-S2M        | ·  | ✓  | ·  | ·  | ·  |
--
-- ✓ = cell filled (this module imports it).
-- · = cell empty (gap in the cone; see "Gaps" section below).
--
-- See `docs/governance/generator_over_orbit.md` for genericization
-- pattern; see the substrate's Coxeter-Fin-Generic / Zn-x-FreeCyclic /
-- Zn-x-FreeCyclic-PhaseProjection / Zn-Coxeter-Strict2Monoid generics
-- for the chain-shape parametric modules that feed these cells.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Manifest where

------------------------------------------------------------------------
-- Coxeter core: word algebras (per-n irreducible data type).
------------------------------------------------------------------------

import Substrate.Groups.Z2-Coxeter
import Substrate.Groups.Z3-Coxeter
import Substrate.Groups.Z4-Coxeter
import Substrate.Groups.Z5-Coxeter
import Substrate.Groups.Z7-Coxeter

------------------------------------------------------------------------
-- Coxeter-Group: Group bundle via Coxeter.GroupAdapter.
------------------------------------------------------------------------

import Substrate.Groups.Z2-Coxeter-Group
import Substrate.Groups.Z3-Coxeter-Group
import Substrate.Groups.Z4-Coxeter-Group
import Substrate.Groups.Z5-Coxeter-Group

------------------------------------------------------------------------
-- Coxeter-Strict2Monoid: Strict2Monoid via Zn-Coxeter-Strict2Monoid.
------------------------------------------------------------------------

import Substrate.Groups.Z3-Coxeter-Strict2Monoid
import Substrate.Groups.Z4-Coxeter-Strict2Monoid
import Substrate.Groups.Z5-Coxeter-Strict2Monoid

------------------------------------------------------------------------
-- Coxeter-Fin: Fin n bijection + action + HasOrderPerm via
-- Coxeter-Fin-Generic.
------------------------------------------------------------------------

import Substrate.Groups.Z3-Coxeter-Fin
import Substrate.Groups.Z4-Coxeter-Fin
import Substrate.Groups.Z5-Coxeter-Fin

------------------------------------------------------------------------
-- x-FreeCyclic: 2-D DirectProduct via Zn-x-FreeCyclic.
------------------------------------------------------------------------

import Substrate.Groups.Z3-x-FreeCyclic
import Substrate.Groups.Z4-x-FreeCyclic
import Substrate.Groups.Z5-x-FreeCyclic

------------------------------------------------------------------------
-- x-FreeCyclic-PhaseProjection: phase-project + homomorphism witnesses
-- via Zn-x-FreeCyclic-PhaseProjection.
------------------------------------------------------------------------

import Substrate.Groups.Z3-x-FreeCyclic-PhaseProjection
import Substrate.Groups.Z4-x-FreeCyclic-PhaseProjection
import Substrate.Groups.Z5-x-FreeCyclic-PhaseProjection

------------------------------------------------------------------------
-- x-FreeCyclic-Degree: ℕ-grading on the cycle axis (single instance).
------------------------------------------------------------------------

import Substrate.Groups.Z3-x-FreeCyclic-Degree

------------------------------------------------------------------------
-- x-FreeCyclic-Strict2Monoid: 2-D Strict2Monoid via direct-product.
------------------------------------------------------------------------

import Substrate.Groups.Z3-x-FreeCyclic-Strict2Monoid

------------------------------------------------------------------------
-- Cross-Zₙ aggregators (orbit consumers, not per-cell capabilities).
------------------------------------------------------------------------

import Substrate.Groups.Z-x-FreeCyclic-PhaseAdvance
import Substrate.Groups.Z-x-FreeCyclic-Recovery
import Substrate.Groups.Z3-x-Z4-x-FreeCyclic
import Substrate.Groups.CyclicCoxeterStrict2Monoids
import Substrate.Groups.ConsolidatedCyclicCoxeter
import Substrate.Groups.TwoDimWordAlgebra

------------------------------------------------------------------------
-- Gaps in the (M, N) cone — capabilities NOT yet supplied per Zₙ.
--
-- Z₂ (involutive, separate from cyclic Z₃+):
--   • Z2-Coxeter-Strict2Monoid    — easy via Zn-Coxeter-Strict2Monoid
--   • Z2-Coxeter-Fin              — Z₂ trivially σ₂ = swap; easy
--   • Z2-x-FreeCyclic*            — easy via Zn-x-FreeCyclic
--
-- Z₇ (only the core landed):
--   • Z7-Coxeter-Group            — easy via Coxeter.GroupAdapter
--   • Z7-Coxeter-Strict2Monoid    — easy via Zn-Coxeter-Strict2Monoid
--   • Z7-Coxeter-Fin              — easy via Coxeter-Fin-Generic
--   • Z7-x-FreeCyclic*            — easy via Zn-x-FreeCyclic
--
-- Z₄ / Z₅ for non-orbit capabilities (single Z₃ instance, not yet
-- promoted to orbit; defer per [[feedback-coalgebraic-not-consumer-driven]]):
--   • Z4-x-FreeCyclic-Degree      / Z5-x-FreeCyclic-Degree
--   • Z4-x-FreeCyclic-Strict2Monoid / Z5-x-FreeCyclic-Strict2Monoid
--
-- Filling any of these gaps is mechanical once the corresponding
-- generic exists (which is the case for all marked "easy" above).
------------------------------------------------------------------------
