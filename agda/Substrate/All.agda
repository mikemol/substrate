------------------------------------------------------------------------
-- Substrate.All
--
-- The substrate's master build target. If this module typechecks,
-- every reachable module in the import graph typechecks.
--
-- Why this exists: there is no single architectural entry point
-- that transitively reaches every substrate module, because the
-- substrate has multiple co-equal top-level subtrees (Foundation
-- as the universe layer; Generators as the generator catalog;
-- Discipline as the inference-rule layer; ShadowArchitecture as
-- the structural-reflection arc; the various arc-final Capstones).
-- This aggregator imports the union of all top-level catalogues
-- + arc capstones, which together cover 100% of the module tree.
--
-- The CONCEPTUAL universal target is the substrate's UP-Topos
-- (Substrate.Category.UniversalProperty.SubstrateTopos): per the
-- UP-arc plan, every universal property is an object in
-- UPCategory, and the topos is the sheaf-of-UPs. Once HC1-HC40
-- populate the topos with concrete UPs as internal objects,
-- SubstrateTopos becomes the structural universal target. Until
-- then, this Substrate.All module serves the practical
-- "if-this-builds-everything-builds" role.
--
-- Per the discipline: each import below is a per-arc or
-- per-domain entry point; nothing here is content-bearing.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.All where

------------------------------------------------------------------------
-- Top-level architectural anchors.
------------------------------------------------------------------------

import Substrate.Foundation
import Substrate.Generators
import Substrate.Discipline
import Substrate.ShadowArchitecture

------------------------------------------------------------------------
-- Category framework catalogues.
------------------------------------------------------------------------

import Substrate.Category.PrimitivesAll
import Substrate.Category.PrimitiveInstances
import Substrate.Category.OrphanAudit

------------------------------------------------------------------------
-- Per-arc manifests.
------------------------------------------------------------------------

import Substrate.Groups.Manifest

------------------------------------------------------------------------
-- Arc-final capstones.
------------------------------------------------------------------------

import Substrate.Algebra.F1.Capstone
import Substrate.Algebra.Module.Capstone
import Substrate.Algebra.Q.Capstone
import Substrate.Algebra.V-Arc.Capstone
import Substrate.Category.FreeLinearizationR.Capstone
import Substrate.Pedagogy.Capstone

------------------------------------------------------------------------
-- Demos.
------------------------------------------------------------------------

import Substrate.Category.Adjunction.Demos
