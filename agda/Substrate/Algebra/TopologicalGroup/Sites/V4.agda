------------------------------------------------------------------------
-- Substrate.Algebra.TopologicalGroup.Sites.V4
--
-- Concrete site: V₄ (Klein four-group) as a topological group with
-- the discrete topology. V₄ is a finite abelian group of order 4;
-- with discrete topology it's a locally compact abelian (LCA) group.
--
-- Ⓒ.v4.site (2026-07-05): this WAS a self-contained `data V4` + a bare
-- 16-entry `V4-op` Cayley table with NO laws, and prose OVERCLAIMING a
-- TopologicalGroup bridge ("the full Group instance ... populated by the
-- runtime concrete instance", "downstream concrete sites supply the full
-- record") — while inhabiting nothing. In fact TopologicalGroup's ONLY
-- field is the group, and the substrate already proves V₄-Group :
-- Group V₄ (Groups.V4.Bundle), so the site is inhabited outright, honestly,
-- below. The carrier is the canonical Groups.V4 V₄ — no reinvention.
--
-- GROUNDED IN THE TOWER: V₄ is not merely the canonical carrier — it is the
-- Klein-four subgroup the witness tower BUILDS at rung 4 (S₄ = perms 4). That
-- V₄'s elements ARE the tower's permutations and its operation IS the tower's
-- `compose` is witnessed in Substrate.WitnessTower.V4Grounding (the embedding
-- ⟦_⟧ into Perm 4 + `·-is-compose`, bisimilar-with-the-build) — the ExtrudeSKI-
-- KFaces "an attribute IS its build-trace" method. (Not imported here: this
-- Algebra-layer site sits below the tower; the grounding is the tower's job.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.TopologicalGroup.Sites.V4 where

open import Substrate.Algebra.Group using (Group)
open import Substrate.Algebra.TopologicalGroup using (TopologicalGroup)
open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Groups.V4.Bundle using (V₄-Group)

------------------------------------------------------------------------
-- The site, inhabited: V₄ as a topological group. The group is the
-- substrate's proven V₄-Group (all Magma/Semigroup/Monoid/Group laws
-- discharged in Groups.V4.Axioms/Bundle); the topology is the trivial
-- discrete marker (TopologicalGroup's only field is the group).
------------------------------------------------------------------------
V4-TopologicalGroup : TopologicalGroup V₄
V4-TopologicalGroup = record { group = V₄-Group }
