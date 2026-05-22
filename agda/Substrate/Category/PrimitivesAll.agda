------------------------------------------------------------------------
-- Substrate.Category.PrimitivesAll
--
-- Capstone module re-exporting the full categorical primitive family.
--
-- After this arc, the substrate's categorical primitives are:
--   #1-#6: original roadmap (all closed)
--   #7-#12: additions across subsequent arcs (Strict2Monoid,
--           GradedMonoid, Cone, FieldBond, FieldTower, FieldFanOut)
--
-- All 12 primitives + Cone family + Bond family + 2-cell calculus.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PrimitivesAll where

------------------------------------------------------------------------
-- Original roadmap primitives.
------------------------------------------------------------------------

import Substrate.Category.Coalgebra
import Substrate.Category.Coalgebra.FiniteOrder
import Substrate.Category.Coalgebra.LagrangeOrder

import Substrate.Category.Equalizer
import Substrate.Category.Pullback
import Substrate.Category.Adjunction
import Substrate.Category.BeckChevalley

import Substrate.Category.FreeLinearization
import Substrate.Category.FreeLinearization.FromImages

------------------------------------------------------------------------
-- BC 2-cell calculus.
------------------------------------------------------------------------

import Substrate.Category.BeckChevalley.Compose
import Substrate.Category.BeckChevalley.Horizontal
import Substrate.Category.BeckChevalley.ComposeInstance

------------------------------------------------------------------------
-- BC concrete instances.
------------------------------------------------------------------------

import Substrate.Category.TensorProduct.BCInstances

------------------------------------------------------------------------
-- Strict2Monoid + GradedMonoid family.
------------------------------------------------------------------------

import Substrate.Category.Strict2Monoid
import Substrate.Category.Strict2Monoid.FromCoxeter
import Substrate.Category.Strict2Monoid.DirectProduct

import Substrate.Category.GradedMonoid
import Substrate.Category.CommutativeMonoid
import Substrate.Category.RGradedMonoid
import Substrate.Category.RGradedMonoid.FromCoxeterHomomorphism

------------------------------------------------------------------------
-- Cone family.
------------------------------------------------------------------------

import Substrate.Category.Cone
import Substrate.Category.Cone.Product
import Substrate.Category.Cone.FieldFilling
import Substrate.Category.Cone.EdgeApex
import Substrate.Category.Cone.WithMorphisms

import Substrate.Category.Cone.EqualizerInstance
import Substrate.Category.Cone.PullbackInstance
import Substrate.Category.Cone.EqualizerWithMorphisms
import Substrate.Category.Cone.PullbackWithMorphisms

------------------------------------------------------------------------
-- Bond family.
------------------------------------------------------------------------

import Substrate.Category.FieldBond
import Substrate.Category.MultiFieldBond
import Substrate.Category.FieldFanOut
import Substrate.Category.FieldContinuum

------------------------------------------------------------------------
-- Torsor family (#13).
--
-- G-torsor universal property: free transitive group action on a set.
-- Captures gauge-freedom spaces (e.g., the 168 Reserved↔SelfDual
-- bridges at HodgeDim4) as single universal-property objects.
------------------------------------------------------------------------

import Substrate.Category.GTorsor

------------------------------------------------------------------------
-- Prime-factored gauge family (#15-#19).
--
-- Universal mechanism for using the multi-chart atlas as bridging
-- equivariance for any construct built from conjugations of prime-
-- numbered fields. Closes [[reserved-selfdual-bijection-gauge]]
-- generically + scales to the Monster.
------------------------------------------------------------------------

import Substrate.Category.SylowDecomposition                          -- #15
import Substrate.Category.PrimeFactoredGauge                          -- #16
import Substrate.Category.PrimeFactoredGauge.MultiRouteEquivariance   -- (theorem on #16)
import Substrate.Category.PresentedGroup                              -- #17
import Substrate.Category.ConjugationCoalgebra                        -- #18
import Substrate.Category.GaloisAdjunction                            -- #19

------------------------------------------------------------------------
-- WithCharacters extension of ConjugationCoalgebra (U1-U2 of next arc).
--
-- Character-table data + orthogonality predicates. Enables substrate-
-- side handling of representation-theoretic content (= the
-- cohomology side of [[homology-cohomology-recursion]]).
------------------------------------------------------------------------

import Substrate.Category.ConjugationCoalgebra.WithCharacters
import Substrate.Category.ConjugationCoalgebra.CharacterOrthogonality

------------------------------------------------------------------------
-- CentralizerDescent (V1 of next arc) — recursive centralizer
-- structure enabling the Happy Family hierarchy from the Monster.
------------------------------------------------------------------------

import Substrate.Category.CentralizerDescent

------------------------------------------------------------------------
-- AbelianPFG (W1 of next arc) — PFG specialization for abelian
-- gauge groups; CRT product decomposition.
------------------------------------------------------------------------

import Substrate.Category.AbelianPFG

------------------------------------------------------------------------
-- Continuum lifts + algebra (X1-X3 of next arc).
--
-- S1-Lift / S2-Lift: discrete-to-continuum constructors for cyclic
-- and projective limits. CommutativeNonAssociativeAlgebra: algebra
-- primitive for Griess + similar commutative-non-associative
-- structures.
------------------------------------------------------------------------

import Substrate.Category.S1-Lift
import Substrate.Category.S2-Lift
import Substrate.Category.CommutativeNonAssociativeAlgebra

------------------------------------------------------------------------
-- Word→InGenerated bridge + PresentedGroup→joint-gen pipeline
-- (Y1 + Y2 of next arc).
--
-- The substrate's universal mechanism for discharging joint-gen
-- via presentation, not enumeration. Per the user's "find the
-- pullback" observation: joint-gen IS word structure.
------------------------------------------------------------------------

import Substrate.Category.SylowDecomposition.FromWord
import Substrate.Category.PrimeFactoredGauge.FromPresented

------------------------------------------------------------------------
-- Grothendieck-closure remediation (Z-arc, Z1-Z5 foundations).
--
-- Closes the substrate's "no morphism layer" gap across primitives
-- + provides Aut(_) + GrothendieckConstruction + DescentTree +
-- CategoryOf primitives.
------------------------------------------------------------------------

import Substrate.Category.Morphism                              -- Z1
import Substrate.Category.AutomorphismGroup                     -- Z2
import Substrate.Category.GrothendieckConstruction              -- Z3
import Substrate.Category.CentralizerDescent.Tree               -- Z4
import Substrate.Category.CategoryOf                            -- Z5
import Substrate.Category.Cone.Morphism                         -- Z6
import Substrate.Category.GTorsor.Morphism                      -- Z7

------------------------------------------------------------------------
-- L-arc primitives — Lie + Grassmann + Hodge algebras (L1-L20).
--
-- Phase Λ (L1-L5): foundational algebra primitives.
--   L1 AntiCommutativeAlgebra — base for Lie + graded ACA
--   L2 LieAlgebra — ACA + Jacobi
--   L3 ExteriorAlgebra — graded free associative + nilpotent deg-1
--   L4 WedgeProduct — rank-2 ergonomic slice
--   L5 GenericHodgeStar — Λᵏ ↔ Λⁿ⁻ᵏ duality
--
-- Phase Λ' morphism layers (L8-L10): Grothendieck-closure for L1-L3.
--   L8 LieAlgebra.Morphism
--   L9 ExteriorAlgebra.Morphism
--   L10 AntiCommutativeAlgebra.Morphism
--
-- Phase Λ'' (L11-L13): Coxeter ↔ Cartan ↔ Lie bridge.
--   L11 RootSystem (combinatorial root data)
--   L12 CartanType (Coxeter matrix)
--   L13 Coxeter.AsCartanType (bridge from Word algebra)
--
-- Phase Λ''' (L16, L18): commutative-non-associative + Lie-adjunction.
--   L16 JordanAlgebra (commutative + Jordan identity)
--   L18 UniversalEnvelopingAlgebra (Lie → Assoc left adjoint)
--
-- Per [[universal-property-discipline]] + [[continuous-via-discrete-
-- inference-rules]]: all L-arc primitives capture structure with
-- abstract carriers; concrete realisations (sl₂, so₃, Bivector,
-- Griess, MonsterLieAlgebra) are downstream module-parametric
-- instances exposed via PrimitiveInstances.
------------------------------------------------------------------------

import Substrate.Category.AntiCommutativeAlgebra                 -- L1
import Substrate.Category.LieAlgebra                             -- L2
import Substrate.Category.ExteriorAlgebra                        -- L3
import Substrate.Category.WedgeProduct                           -- L4
import Substrate.Category.GenericHodgeStar                       -- L5
import Substrate.Category.LieAlgebra.Morphism                    -- L8
import Substrate.Category.ExteriorAlgebra.Morphism               -- L9
import Substrate.Category.AntiCommutativeAlgebra.Morphism        -- L10
import Substrate.Category.RootSystem                             -- L11
import Substrate.Category.CartanType                             -- L12
import Substrate.Category.Coxeter.AsCartanType                   -- L13 (parametric)
import Substrate.Category.JordanAlgebra                          -- L16
import Substrate.Category.UniversalEnvelopingAlgebra             -- L18

------------------------------------------------------------------------
-- M-arc primitives — functorial closure of the L-arc (M1-M10).
--
-- Per [[grothendieck-coherence-rule]]: every "X ↦ S(X)" substrate
-- assignment must be Functor-ified or it surfaces as a hidden orphan
-- on the next Grothendieck lift. M1-M4 supply the higher-categorical
-- carriers (Functor + NaturalTransformation + SymmetricMonoidal +
-- Dagger); M5-M9 close the specific L-arc orphan gaps.
--
--   M1 Functor — 1-cells of Cat
--   M2 NaturalTransformation — 2-cells of Cat
--   M3 SymmetricMonoidal — ⊗ + I + σ + σ-involution
--   M4 DaggerCategory — †² = id involutive structure
--
-- M5-M9 are concrete-bridge modules and live in PrimitiveInstances.
------------------------------------------------------------------------

import Substrate.Category.Functor                                -- M1
import Substrate.Category.NaturalTransformation                  -- M2
import Substrate.Category.SymmetricMonoidal                      -- M3
import Substrate.Category.DaggerCategory                         -- M4
import Substrate.Category.OrphanAudit                            -- M10 (audit doc)

------------------------------------------------------------------------
-- Q-arc primitives (higher categories): Q1 TwoCategory, Q2 Modification
-- (3-cells), Q6 PseudoFunctor, Q7 LaxFunctor, Q8 TwoNatTrans, Q9
-- TwoEquivalence. Q3/Q4/Q5 are concrete-bridge modules (in
-- PrimitiveInstances).
------------------------------------------------------------------------

import Substrate.Category.TwoCategory                            -- Q1
import Substrate.Category.Modification                           -- Q2
import Substrate.Category.PseudoFunctor                          -- Q6
import Substrate.Category.LaxFunctor                             -- Q7
import Substrate.Category.TwoNaturalTransformation               -- Q8
import Substrate.Category.TwoEquivalence                         -- Q9

------------------------------------------------------------------------
-- R-arc primitives (monads / operads / VOAs): R1 Monad, R2 Comonad,
-- R3 Algebra-of-Monad, R4 Coalgebra-of-Comonad, R5 Kleisli, R6 EM,
-- R7 Operad, R8 VertexOperatorAlgebra.
------------------------------------------------------------------------

import Substrate.Category.Monad                                  -- R1
import Substrate.Category.Comonad                                -- R2
import Substrate.Category.Algebra-of-Monad                       -- R3
import Substrate.Category.Coalgebra-of-Comonad                   -- R4
import Substrate.Category.Monad.DerivedCategoryOf                -- R5/R6 skeleton
import Substrate.Category.KleisliCategory                        -- R5
import Substrate.Category.EilenbergMooreCategory                 -- R6
import Substrate.Category.Operad                                 -- R7
import Substrate.Category.VertexOperatorAlgebra                  -- R8

------------------------------------------------------------------------
-- S-arc primitives (geometric/topos infrastructure): S1 Sheaf, S2
-- Limit (generic), S3 Colimit, S4 KanExtension, S5 PresheafCategory,
-- S6 YonedaEmbedding, S7 SubobjectClassifier, S8 Topos, S9 Groupoid-
-- Cardinality.
------------------------------------------------------------------------

import Substrate.Category.Sheaf                                  -- S1
import Substrate.Category.Limit                                  -- S2
import Substrate.Category.Colimit                                -- S3
import Substrate.Category.KanExtension                           -- S4
import Substrate.Category.PresheafCategory                       -- S5
import Substrate.Category.YonedaEmbedding                        -- S6
import Substrate.Category.SubobjectClassifier                    -- S7
import Substrate.Category.Topos                                  -- S8
import Substrate.Category.GroupoidCardinality                    -- S9

------------------------------------------------------------------------
-- Roadmap documentation modules.
------------------------------------------------------------------------

import Substrate.Category.PrimitivesRoadmapV2

------------------------------------------------------------------------
-- Capstone.
--
-- After this slice: a single import-target for the full categorical
-- primitive family. Downstream code can `import Substrate.Category.
-- PrimitivesAll` to bring everything into scope (transitively).
--
-- 10-slice arc summary:
--
--   #1 FreeLinearization record (closes original roadmap #6)
--   #2 FreeLinearization.FromImages constructor
--   #3 project_freelinearization_names_linear_from_images memory
--   #4 Cone.WithMorphisms primitive (base-internal morphisms)
--   #5 Cone.EqualizerWithMorphisms (Equalizer first-class parallel pair)
--   #6 Cone.PullbackWithMorphisms (Pullback first-class cospan)
--   #7 FieldFanOut primitive (fan-out tree bonds)
--   #8 project_tree_shaped_field_bonds memory
--   #9 PrimitivesRoadmapV2 documentation
--   #10 THIS PrimitivesAll re-export.
--
-- Per [[project-cone-subsumes-equalizer-pullback]] + project_
-- freelinearization_names_linear_from_images + project_tree_shaped_
-- field_bonds: the substrate's categorical infrastructure is now
-- comprehensive across cones, free linearization, and multi-field
-- bond decompositions.
--
-- The original 6-primitive roadmap is closed. Subsequent arcs
-- (#7-#12) added Strict2Monoid + GradedMonoid + Cone + Bond
-- families.
--
-- Next natural arcs (deferred):
--   * Concrete FreeLinearization instances at substrate sites
--     (re-cast existing linear-from-images uses).
--   * Higher-arity Cone.WithMorphisms (e.g., V₄'s 3+1 with internal
--     morphisms).
--   * Generic FieldTree (arbitrary DAG of bonds).
--   * BC interchange law (vertical + horizontal commute formally).
------------------------------------------------------------------------
