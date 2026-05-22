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
-- Joint-gen-via-presentation instances (Y3-Y9 of next arc).
--
-- Replaces W4's "168-case enumeration" scaffold with the substrate's
-- universal-property approach: every group's joint-gen is dischargeable
-- via its presentation + Y2's pipeline.
--
-- Per the user's "find the pullback" observation: NO enumeration
-- anywhere; joint-gen IS word structure (Y1 + Y2).
------------------------------------------------------------------------

import Substrate.Algebra.GL3F2.AsPresented                     -- Y3
import Substrate.Algebra.GL3F2.JointGenViaPresentation         -- Y4
import Substrate.Algebra.Abelian.Z6JointGenViaProduct          -- Y5
import Substrate.Algebra.Abelian.Z30JointGenViaProduct         -- Y6
import Substrate.Algebra.Sporadic.Monster.AsPresented          -- Y7+Y8
import Substrate.Algebra.Sporadic.HappyFamily.JointGenViaDescent  -- Y9

------------------------------------------------------------------------
-- Grothendieck-closure instances (Z-arc, Z8 + Z9).
--
-- Happy Family as single descent-tree object (Z8) + Monster
-- reconstructed as Aut(GriessAlgebra) via Z2 (Z9). Closes
-- Gaps #2 and #3 from the Grothendieck-closure audit.
------------------------------------------------------------------------

import Substrate.Algebra.Sporadic.HappyFamily.AsTree           -- Z8
import Substrate.Algebra.Sporadic.GriessAlgebra.Aut            -- Z9

------------------------------------------------------------------------
-- FieldContinuum primitive (#14) — exposed as a primitive but no
-- substrate-side instances yet. Per
-- [[continuous-via-discrete-inference-rules]]: domain-specific
-- instances (Fluidic / Magnetic / Photonic) supply the Continuum
-- target as an abstract Set; not in scope as substrate-side content.
------------------------------------------------------------------------

import Substrate.Category.FieldContinuum

------------------------------------------------------------------------
-- L-arc instances (Lie + Grassmann + Hodge structures).
--
-- Bridges from existing substrate sites + module-parametric instance
-- modules:
--
--   L6 Bivector.AsExterior — HodgeDim4 Λ²(F₂⁴) as L4 WedgeProduct
--      instance (supplies the wedge pairing missing from the original
--      Bivector module).
--   L7 HodgeStar.AsGenericHodge — HodgeDim4 ★ as L5 GenericHodgeStar
--      instance; fifth universal-property view of the canonical ★.
--   L14 sl₂ — module-parametric L2 LieAlgebra at Cartan type A₁.
--   L15 so₃ — module-parametric L2 LieAlgebra at A₁ with angular-
--      momentum basis (sibling of sl₂).
--   L17 GriessAlgebra.AsJordan — parametric bridge; substrate does
--      NOT assert Griess is Jordan (see L17 caveat).
--   L19 MonsterLieAlgebra — module-parametric L2 LieAlgebra at the
--      Borcherds-Kac-Moody m (Borcherds 1992).
--
-- All parametric per substrate convention; consumers supply the
-- concrete realisation data.
------------------------------------------------------------------------

import Substrate.Algebra.F2.HodgeDim4.Bivector.AsExterior        -- L6
import Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsGenericHodge   -- L7
import Substrate.Algebra.Lie.sl2                                  -- L14 (parametric)
import Substrate.Algebra.Lie.so3                                  -- L15 (parametric)
import Substrate.Algebra.Sporadic.GriessAlgebra.AsJordan          -- L17 (parametric)
import Substrate.Algebra.Sporadic.MonsterLieAlgebra               -- L19 (parametric)

------------------------------------------------------------------------
-- M-arc functorial-closure bridges (M5-M9).
--
-- Per [[grothendieck-coherence-rule]]: each module lifts a previous
-- L-arc primitive from "record-instance" to "M1 Functor" or "M2
-- NaturalTransformation," closing latent orphan gaps.
--
--   M5 ExteriorAlgebra.AsFunctor — Λ : Vect → ExtAlg as Functor
--   M6 LieAlgebra.AsFunctor — U_Lie : Assoc → Lie as Functor
--   M7 UniversalEnvelopingAlgebra.AsFunctor — U : Lie → Assoc as Functor
--   M8 Coxeter.AsCartanType.Functor — L13 lifted to functorial action
--   M9 HodgeStar.AsNaturalTransformation — ★ as M2 nat-trans, closing
--      "★ commutes with wedge-morphisms" as the naturality square
--
-- All parametric; consumers supply the concrete CategoryOf instances
-- + functor/nat-trans data per substrate convention.
------------------------------------------------------------------------

import Substrate.Category.ExteriorAlgebra.AsFunctor                    -- M5
import Substrate.Category.LieAlgebra.AsFunctor                          -- M6
import Substrate.Category.UniversalEnvelopingAlgebra.AsFunctor          -- M7
import Substrate.Category.Coxeter.AsCartanType.Functor                  -- M8
import Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsNaturalTransformation -- M9

------------------------------------------------------------------------
-- N-arc functorial closures of M-arc audit (N1-N9).
--
-- Each N-arc slice closes one OrphanAudit row (= one substrate
-- mechanism that was implicit "X ↦ S(X)" but not named as M1
-- Functor / M2 NaturalTransformation / M3 SymmetricMonoidal / M4
-- DaggerCategory).
--
--   N1 AutomorphismGroup.AsFunctor — Z2 Aut as M1 Functor
--   N2 CategoryOf.AsFunctor — Z5 CategoryOf as M1 Functor
--   N3 GrothendieckConstruction.AsFunctor — Z3 ∫ as M1 Functor
--   N4 PrimeFactoredGauge.AsFunctor — T7 PFG as M1 Functor
--   N5 S1-Lift.AsFunctor — X1 S¹-Lift as M1 Functor
--   N6 S2-Lift.AsFunctor — X2 S²-Lift as M1 Functor
--   N7 F2.Linear.AsSymmetricMonoidal — F₂-Linear as M3 instance
--   N8 F2.Linear.AsDaggerCategory — F₂-Linear as M4 instance
--   N9 GaloisAdjunction.UnitCounit — η + ε as M2 nat-trans
------------------------------------------------------------------------

import Substrate.Category.AutomorphismGroup.AsFunctor              -- N1
import Substrate.Category.CategoryOf.AsFunctor                     -- N2
import Substrate.Category.GrothendieckConstruction.AsFunctor       -- N3
import Substrate.Category.PrimeFactoredGauge.AsFunctor             -- N4
import Substrate.Category.S1-Lift.AsFunctor                        -- N5
import Substrate.Category.S2-Lift.AsFunctor                        -- N6
import Substrate.Algebra.F2.Linear.AsSymmetricMonoidal             -- N7
import Substrate.Algebra.F2.Linear.AsDaggerCategory                -- N8
import Substrate.Category.GaloisAdjunction.UnitCounit              -- N9

------------------------------------------------------------------------
-- O-arc (O1-O10): compound functors, Monster-as-Grothendieck, Cartan↔
-- Root equivalence, Jordan→CNAA forgetful + capstone.
------------------------------------------------------------------------

import Substrate.Algebra.F2.Linear.AsCompactClosed                 -- O1
import Substrate.Category.GrothendieckOfAut                        -- O2
import Substrate.Category.PrimeFactoredGauge.ActedUponByAut        -- O3
import Substrate.Category.GaloisAdjunction.AsAdjunction            -- O4
import Substrate.Algebra.Sporadic.Monster.AsGrothendieckObject     -- O5
import Substrate.Category.CartanType.AsRootSystem                  -- O6
import Substrate.Category.RootSystem.AsCartanType                  -- O7
import Substrate.Category.CartanRootEquivalence                    -- O8
import Substrate.Category.JordanAlgebra.UnderlyingCNAA             -- O9

------------------------------------------------------------------------
-- P-arc (P1-P10): Hodge-dagger and bijection structures, F₂-Linear
-- abelian/exact category, HodgeDim4 as groupoid.
------------------------------------------------------------------------

import Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsDaggerEndomap            -- P1
import Substrate.Algebra.F2.Linear.Bijection.AsDagger                       -- P2
import Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor.AsNaturalTransformation  -- P3
import Substrate.Algebra.F2.Linear.AsRigidCategory                          -- P4
import Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsSelfDualMorphism          -- P5
import Substrate.Algebra.F2.HodgeDim4.Bivector.AsCompactClosedDual          -- P6
import Substrate.Algebra.F2.HodgeDim4.AsGroupoid                            -- P7
import Substrate.Algebra.F2.Linear.AsAbelianCategory                        -- P8
import Substrate.Algebra.F2.Linear.AsExactCategory                          -- P9

------------------------------------------------------------------------
-- Q-arc concrete-bridge modules (Q3 ∫ as 2-functor, Q4 Cat as 2-cat,
-- Q5 Adjunction as 2-cell structure).
------------------------------------------------------------------------

import Substrate.Category.GrothendieckConstruction.AsTwoFunctor    -- Q3
import Substrate.Category.Cat.AsTwoCategory                        -- Q4
import Substrate.Category.Adjunction.AsTwoCellStructure            -- Q5

------------------------------------------------------------------------
-- R-arc instance modules (R9 V♮ as VOA).
------------------------------------------------------------------------

import Substrate.Algebra.Sporadic.MonsterVOA                       -- R9

------------------------------------------------------------------------
-- Recently-landed primitives (skeleton-as-pullback witnesses + duals).
--
-- Opposite + Functor.Opposite: the duality-witness primitives.
-- Coequalizer + Pushout: Set-level duals of Equalizer + Pullback.
-- *.AsNamed: 1:N cone witnesses for substrate-named structures.
------------------------------------------------------------------------

import Substrate.Category.Opposite
import Substrate.Category.Functor.Opposite
import Substrate.Category.Coequalizer
import Substrate.Category.Pushout
import Substrate.Category.DaggerCategory.AsNamed
import Substrate.Category.SymmetricMonoidal.AsNamed

------------------------------------------------------------------------
-- Orphan-audit sweep: uplink children whose parent is content-bearing
-- (re-export from parent would cycle). Routed through this catalog
-- so each child is reachable. Children stay file-per-lemma per
-- [[s3-on-v4-file-per-lemma]].
------------------------------------------------------------------------

-- F₂ subtree.
import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives
import Substrate.Algebra.F2.Transfer
import Substrate.Algebra.F2.V4LagrangeInstance
import Substrate.Algebra.F2.Code.Universal
import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations
import Substrate.Algebra.F2.HodgeDim3.MetricGauge.ExemplarOrbits
import Substrate.Algebra.F2.HodgeDim3.MetricGauge.V4PlaneOrth
import Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor
import Substrate.Algebra.F2.HodgeDim4.MetricGauge.NonDegenerate
import Substrate.Algebra.F2.Polynomial.Utilities
import Substrate.Algebra.F2.Polynomial.Wedge

-- PontryaginDual + Quotient subtree.
import Substrate.Algebra.PontryaginDual.Category
import Substrate.Algebra.Quotient.CRT
import Substrate.Algebra.Quotient.PhaseB
import Substrate.Algebra.Quotient.V4Cosets

-- Category subtree.
import Substrate.Category.CascadedCoalgebra.Category
import Substrate.Category.Coalgebra.StructuralGCD
import Substrate.Category.Comonoid.Category
import Substrate.Category.DiscreteFourierTransform.Category
import Substrate.Category.FreeLinearizationR.AsModule
import Substrate.Category.StochasticLens.Category
import Substrate.Category.StochasticLens.Eval
import Substrate.Category.TensorProduct.Bilinearity

-- Cocycles/V4Signature subtree.
import Substrate.Cocycles.V4Signature.OrbitKey.Structural
import Substrate.Cocycles.V4Signature.S4GroupIso
import Substrate.Cocycles.V4Signature.S4Iso-Bridges
import Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection
import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivector
import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorCardinality

-- Probability subtree.
import Substrate.Probability.ConjugateMonad.Category
import Substrate.Probability.MarkovCategory.Category
import Substrate.Probability.MarkovCategory.Eval

------------------------------------------------------------------------
-- Orphan-sweep round 2: children previously blocked by build errors,
-- now unblocked via Foundation refactors:
--   * Foundation.Nat._^_       — needed by Cone.FieldFilling
--   * Foundation.Vec polymorph — needed by ChainDecomposition,
--     IsoBCSquare, TensorProduct.Antisymmetric, etc.
--   * Foundation.Vec.tabulate  — needed by SymBilinForm.TensorProductBridge
--   * SymBilinForm.CongruenceCompose Data.Nat drop — unblocks S3Stabiliser
--   * Poly.Connections 0ℓ→0ℓ
--   * ShadowArchitecture.Persistence Data.Bool drop — unblocks Raven
------------------------------------------------------------------------

import Substrate.Algebra.GL3F2.AsChainDecomp
import Substrate.Algebra.F2.Universal
import Substrate.Algebra.F2.HodgeDim3.MetricGauge.S3Stabiliser
import Substrate.Algebra.F2.HodgeDim4.Bivector.IsoBCSquare
import Substrate.Algebra.F2.SymBilinForm.TensorProductBridge
import Substrate.Category.Poly.Category
import Substrate.Category.Poly.Connections
import Substrate.Category.PolyLens.Eval
import Substrate.Category.TensorProduct.Antisymmetric
import Substrate.ShadowArchitecture.Raven

-- Cardinality.Product: unblocked by substrate-native *↔× (d064c8e).
import Substrate.Cardinality.Product

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
