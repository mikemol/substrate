------------------------------------------------------------------------
-- Substrate.Category.PrimitiveInstances
--
-- Catalogue of concrete substrate-level instances of the categorical
-- primitives. Re-export module collecting the instance modules across
-- the substrate.
--
-- After this module, the substrate's categorical primitives have
-- visible per-site instances, not just abstract type definitions.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PrimitiveInstances where

------------------------------------------------------------------------
-- BCSquare instances (Substrate.Category.TensorProduct.BCInstances).
--
--   * poly-mult-BCSquare        (TensorProduct primitive #5 instance)
--   * bilinform-eval-BCSquare   (bilinear form via tensor)
--   * bivector-roundtrip-BCSquare (section/round-trip)
------------------------------------------------------------------------

import Substrate.Category.TensorProduct.BCInstances

------------------------------------------------------------------------
-- Cone primitive instances (#9).
------------------------------------------------------------------------

-- Discrete-base cones:
import Substrate.Algebra.F2.Cone-V4-3plus1
import Substrate.Algebra.F2.Cone-Hamming-7plus1
import Substrate.Algebra.F2.HodgeDim4.Cone-HodgeStar-EdgeApex

-- WithMorphisms cones (generic + substrate instance):
import Substrate.Category.Cone.EqualizerWithMorphisms
import Substrate.Category.Cone.PullbackWithMorphisms
import Substrate.Algebra.F2.HodgeDim4.HodgeStar-ConeWithMorphisms

------------------------------------------------------------------------
-- FieldBond + Tower + FanOut instances.
------------------------------------------------------------------------

import Substrate.Algebra.Z6-FieldBond
import Substrate.Algebra.Z6-FieldTower
import Substrate.Algebra.PrimeFactor-168-FieldFanOut

------------------------------------------------------------------------
-- FreeLinearization instances (#6).
------------------------------------------------------------------------

import Substrate.Algebra.F2.HodgeDim4.HodgeStar-FreeLinearization
import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3-FreeLinearization

------------------------------------------------------------------------
-- Strict2Monoid + GradedMonoid instances.
------------------------------------------------------------------------

-- Per [[Substrate.Groups.CyclicCoxeterStrict2Monoids]] for the
-- comprehensive cyclic instance catalogue (Z₃/Z₄/Z₅, V₄, FreeCyclic,
-- 2-D direct products).
import Substrate.Groups.CyclicCoxeterStrict2Monoids

-- F₂-graded instances on V₄ (length-parity, count-A, count-B) and
-- Bivector (weight-parity).
import Substrate.Groups.V4-Coxeter-F2Graded
import Substrate.Groups.V4-Coxeter-F2Graded-CountA
import Substrate.Groups.V4-Coxeter-F2Graded-CountB
import Substrate.Algebra.F2.HodgeDim4.Bivector-F2Graded

------------------------------------------------------------------------
-- Order-k Coxeter instances.
------------------------------------------------------------------------

-- Cyclic Coxeter at small n + word-to-Fin bridges (per
-- Substrate.Groups.ConsolidatedCyclicCoxeter).
import Substrate.Groups.ConsolidatedCyclicCoxeter

------------------------------------------------------------------------
-- GTorsor instances (#13).
--
-- Universal-property unification of gauge-freedom spaces. Each GTorsor
-- instance packages a discrete gauge family as a single torsor
-- (free transitive group action on a set).
--
-- HodgeDim4 instance: the 168 Reserved↔SelfDual F₂-linear bijections
-- as a GL(3, F₂)-torsor, with named representatives anchoring each
-- Sylow-classification layer. See AtlasCatalogue for the full re-export
-- of named witnesses (canonical, alt-A/B-orbit, swap01/cycle3/singer-
-- bridges, Hodge-★-trivial-action).
------------------------------------------------------------------------

import Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor
import Substrate.Algebra.F2.HodgeDim4.ReservedBridge.AlternativesAsOrbit
import Substrate.Algebra.F2.HodgeDim4.ReservedBridge.SylowOrbitWitnesses
import Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsGaugeAction
import Substrate.Algebra.F2.HodgeDim4.ReservedBridge.AtlasCatalogue

------------------------------------------------------------------------
-- Supporting primitives (Linear/Bijection + GL3F2 from prior arcs).
--
-- Substrate.Algebra.F2.Linear.Bijection: F₂-linear bijection primitive
-- (forward + backward + two-sided inverse witnesses); foundational
-- for GaugeTorsor and any other torsor at F₂-Vect.
--
-- Substrate.Algebra.GL3F2.* — full multi-route equivariance arc;
-- imported here so PrimitiveInstances exposes the gauge-group
-- infrastructure as part of the catalog.
------------------------------------------------------------------------

import Substrate.Algebra.F2.Linear.Bijection
import Substrate.Algebra.GL3F2
import Substrate.Algebra.GL3F2.GaugeGenerators
import Substrate.Algebra.GL3F2.SingerOrder
import Substrate.Algebra.GL3F2.MultiRouteEquivariance

------------------------------------------------------------------------
-- PrimeFactoredGauge instances (#16) — substrate's first concrete
-- PFG instance + supporting Sylow decomposition.
------------------------------------------------------------------------

import Substrate.Algebra.GL3F2.SylowDecomposition                    -- T6
import Substrate.Algebra.F2.HodgeDim4.ReservedBridge.AsPFG           -- T7

------------------------------------------------------------------------
-- ConjugationCoalgebra instances (#18) — extreme-case demonstration.
--
-- Sporadic.Monster.AsCoalgebra: the Monster as a ConjugationCoalgebra,
-- module-parametric in ATLAS class data. Demonstrates the substrate's
-- top-down framework scales to the largest sporadic simple group.
------------------------------------------------------------------------

import Substrate.Algebra.Sporadic.Monster.AsCoalgebra                -- T8

------------------------------------------------------------------------
-- WithCharacters instances (U3, U4 of next arc).
--
-- GL3F2.Characters: concrete 6×6 character table for GL(3, F₂) ≅
-- PSL(2, 7). The substrate's first concrete WithCharacters-style
-- data (32 of 36 cells correctly populated as ℤ; 4 algebraic cells
-- marked as placeholders).
--
-- Monster.WithCharacters: parametric placeholder for the Monster's
-- 194 × 194 character data; concrete data is external.
------------------------------------------------------------------------

import Substrate.Algebra.GL3F2.Characters
import Substrate.Algebra.Sporadic.Monster.WithCharacters

------------------------------------------------------------------------
-- HappyFamily — 20 sporadic groups (V2-V5 of next arc).
--
-- All Happy Family members as parametric ConjugationCoalgebras:
-- Monster + BabyMonster + Conway × 3 + Mathieu × 5 + Fischer × 3
-- + HN/Th/He/J₂/HS/McL/Suz. The substrate now spans half of the
-- 26 sporadic simple groups (the 6 Pariahs documented but out of
-- scope).
------------------------------------------------------------------------

import Substrate.Algebra.Sporadic.HappyFamily

------------------------------------------------------------------------
-- AbelianPFG instances (W2-W4 of next arc).
--
-- CRT-abelian PrimeFactoredGauge instances at small primes (Z/6,
-- Z/30) + GL(3, F₂) joint-gen scaffold.
------------------------------------------------------------------------

import Substrate.Algebra.Abelian.Z6-as-PFG
import Substrate.Algebra.Abelian.Z30-as-PFG
import Substrate.Algebra.GL3F2.JointGenScaffold

------------------------------------------------------------------------
-- Griess algebra + Monster identification (X4-X5 of next arc).
--
-- The 196,884-dim Griess algebra (Griess 1982; FLM 1988 V♮ weight-2)
-- as a CommutativeNonAssociativeAlgebra instance + Monster ≅
-- Aut(GriessAlgebra) identification module. Closes the substrate-
-- side bridge to the canonical top-down Monster construction.
------------------------------------------------------------------------

import Substrate.Algebra.Sporadic.GriessAlgebra
import Substrate.Algebra.Sporadic.Monster.AsGriessAlgebra

------------------------------------------------------------------------
-- FieldContinuum primitive (#14) — exposed as a primitive but no
-- substrate-side instances yet. Per
-- [[continuous-via-discrete-inference-rules]]: domain-specific
-- instances (Fluidic / Magnetic / Photonic) supply the Continuum
-- target as an abstract Set; not in scope as substrate-side content.
------------------------------------------------------------------------

import Substrate.Category.FieldContinuum

------------------------------------------------------------------------
-- Capstone.
--
-- After this module: an import-target for the FULL set of substrate-
-- level instances of the categorical primitives. Combined with
-- PrimitivesAll (primitive definitions + combinators), the substrate
-- exposes both the abstract framework AND its concrete instantiations
-- at a single import-point.
--
-- Per [[project-cones-at-substrate-sites]] +
-- [[project-freelinearization-substrate-sites]]: the primitives are
-- not just type definitions; they're realized at substrate sites with
-- concrete content.
------------------------------------------------------------------------
