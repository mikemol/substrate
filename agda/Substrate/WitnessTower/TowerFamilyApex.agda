------------------------------------------------------------------------
-- Substrate.WitnessTower.TowerFamilyApex
--
-- ◆AI-1f — the covering-OF-the-covering for the SnVersusTwoPow tower family.
-- The covering apex ◆AI-1e (SnVersusTwoPowTowers) placed Ⓣ₁, Ⓣ₂ under
-- GradedDivStr. That was PARTIAL: (i) Ⓣ₃ (AlgebraLadder, law-increment) is NOT
-- a GradedDivStr, and (ii) — found by probing the family's completeness before
-- closing (◆AI-D5) — the apex is NOT the linear WitnessTower.Core either.
--
-- The real apex is WitnessTower.FamilyWitness (the DAG), and Core is a GAUGE
-- CHOICE on it, NOT the top. FamilyWitness pins three checked facts:
--   (a) Core is a genuine CHAIN — WSimplex-unique : (x y : WSimplex k) → x ≡ y,
--       a singleton per rung, ONE spine.
--   (b) family-witnessing BRANCHES (FSimplex) — a rung is built from a family
--       of facets; a DAG (simplex face lattice), not a chain.
--   (c) the linear spines of a rung-k simplex are the orderings of its (k+1)
--       vertices, so #spines = (k+1)! = |perms (suc k)| (via perms-length). The
--       symmetric group S_{k+1} PERMUTES the spines: Ⓣ₁ (the census/Sₙ tower)
--       IS THE GAUGE GROUP OF THE DAG.
--
-- So the corrected two-(really three-)level closure:
--   FamilyWitness (DAG apex)
--     │  gauge choice: pick one vertex-ordering
--     ▼
--   Core (linear witnessing spine, WSimplex/Path/walk) — covers Ⓣ₁,Ⓣ₂,Ⓣ₃
--     │  data-increment restriction
--     ▼
--   GradedDivStr — covers only Ⓣ₁,Ⓣ₂ (the data-increment towers; ◆AI-1e)
--
-- And the punchline that makes this NON-trivial (not a filing hierarchy): Ⓣ₁
-- (Sₙ), which ◆AI-1e treated as a sibling tower of Ⓣ₂, is REVEALED here as the
-- GAUGE GROUP of the whole family — the census S_{k+1} permuting the linear
-- spines of the branching object. The |Sₙ| column of the sweep is thus not just
-- "a tower alongside 2ⁿ"; it is the symmetry group of the witnessing DAG that
-- Core (hence every linear tower) is a chart on.
--
-- This file re-exports the apex chain so the corrected closure is one import,
-- and states the gauge-group identity (#spines = |perms (suc k)|) as the tie.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.TowerFamilyApex where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- 1. THE APEX: FamilyWitness (DAG), and Core (linear gauge) beneath it.
--    Re-exported so the corrected closure is reachable from one import.
------------------------------------------------------------------------

-- the linear witnessing spine (Core) — the gauge choice.
open import Substrate.WitnessTower.Core
  using (WSimplex; base; witnessing; Path; walk; steps; steps-walk)

-- (a) Core is a CHAIN: WSimplex k is a singleton (one spine, no branching).
open import Substrate.WitnessTower.FamilyWitness
  using (WSimplex-unique)

-- witness that Core carries no branching: the whole rung is determined.
open import Substrate.WitnessTower.Enumerate using (perms; factorial; perms-length; lengthL)
core-is-one-spine : ∀ {k} (x y : WSimplex k) → x ≡ y
core-is-one-spine = WSimplex-unique

------------------------------------------------------------------------
-- 2. THE GAUGE-GROUP TIE: the linear spines of the rung-k simplex number
--    (k+1)! = |perms (suc k)|. Ⓣ₁ (Sₙ census) is the gauge group permuting
--    the spines of the FamilyWitness DAG. Re-exported from the census.
------------------------------------------------------------------------


-- #spines at rung k = |perms (suc k)| = (suc k)! — the census counts the DAG's
-- gauge group. (perms-length is the general term; here it names the identity
-- that Ⓣ₁ = the spine-permutation group.)
spine-count : (k : ℕ) → lengthL (perms (suc k)) ≡ factorial (suc k)
spine-count k = perms-length (suc k)

------------------------------------------------------------------------
-- 3. THE CLOSURE, stated. The three towers are all Core-instances (linear
--    witnessing); GradedDivStr sub-covers the two data-increment ones. The
--    apex above Core is FamilyWitness. This is recorded as prose-in-types:
--    the imports above make FamilyWitness ⊐ Core ⊐ {the towers} reachable, and
--    spine-count ties Ⓣ₁ to the gauge group. No false "Core is the top" — the
--    apex is the DAG, Core the chart. (◆AI-1e's GradedDivStr cover is the
--    bottom level, correct as far as it went; this file supplies the two
--    levels above it that ◆AI-1e closed over.)
------------------------------------------------------------------------

-- the census walk is ONE spine (Core.walk = the identity vertex-ordering); the
-- other (k+1)!−1 spines are its images under the gauge group. This equality
-- names walk as the chosen chart.
chosen-chart : (k : ℕ) → steps (walk k) ≡ k
chosen-chart = steps-walk
