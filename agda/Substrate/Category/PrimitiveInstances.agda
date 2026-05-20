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
