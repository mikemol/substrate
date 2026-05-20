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
