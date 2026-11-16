------------------------------------------------------------------------
-- Substrate.ShadowArchitecture
--
-- Aggregating module for the shadow-architecture arc per
-- `scratch/shadow_architecture_agda_arc_plan.md`. The source artefact
-- is `scratch/shadow-architecture.md` (1605-line trilingual
-- structural rendering).
--
-- Arc complete (all six slices land):
--
--   FanoLabeling    — bit-pattern / sequential aliases over
--                     `Substrate.Algebra.F2.FanoPlane`.
--   Duality         — `normal-vector : FanoLine → Point` and its inverse,
--                     orthogonality proofs.
--   Weight          — Hamming weight + three-orbit partition.
--   SelfReference   — ★ L₆-normal=110, L₇-normal=111, the wt-3 fixed
--                     pair non-incidence.
--   AxisDualLine    — `axis-dual : Axis → FanoLine`.
--   Mode            — decomp / snap / regroup / guard as line-subsets
--                     with coverage theorem; guard territory =
--                     star of 001.
--   Charter         — Realizability 5-cell record (Constructible /
--                     Reachable / Observable / Coverable +
--                     Persists-via).
--   Distinction     — six-row audit table; every distinction passes
--                     the four (+ time-extension) gates.
--   Symmetry        — S₃ ⊂ Aut(Fano) = PSL(2,7); 168 = 6 × 28 coset
--                     count; constructible-vs-reachable verdict;
--                     wt-3 fixed-pair uniqueness theorems.
--   Loop            — Steps A-E AST + W1-W6 warnings + warning-to-gate
--                     mapping + L₆-routing fact for 001 → 110.
--   Persistence     — Cotype as record + monotonic _⊑_ preorder +
--                     populate-point / populate-line monotonicity;
--                     the W5 deletion-prohibition realised at the
--                     type level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture where

open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.ShadowArchitecture.Duality.Bot
open import Substrate.ShadowArchitecture.Duality.DualLine
open import Substrate.ShadowArchitecture.Duality.DualLineNormal
open import Substrate.ShadowArchitecture.Duality.LineCover
open import Substrate.ShadowArchitecture.Duality.NormalDualLine
open import Substrate.ShadowArchitecture.Duality.NormalVector
open import Substrate.ShadowArchitecture.Duality.OrthogonalL1A
open import Substrate.ShadowArchitecture.Duality.OrthogonalL1B
open import Substrate.ShadowArchitecture.Duality.OrthogonalL1C
open import Substrate.ShadowArchitecture.Duality.OrthogonalL2A
open import Substrate.ShadowArchitecture.Duality.OrthogonalL2B
open import Substrate.ShadowArchitecture.Duality.OrthogonalL2C
open import Substrate.ShadowArchitecture.Duality.OrthogonalL3A
open import Substrate.ShadowArchitecture.Duality.OrthogonalL3B
open import Substrate.ShadowArchitecture.Duality.OrthogonalL3C
open import Substrate.ShadowArchitecture.Duality.OrthogonalL4A
open import Substrate.ShadowArchitecture.Duality.OrthogonalL4B
open import Substrate.ShadowArchitecture.Duality.OrthogonalL4C
open import Substrate.ShadowArchitecture.Duality.OrthogonalLA
open import Substrate.ShadowArchitecture.Duality.OrthogonalLA2
open import Substrate.ShadowArchitecture.Duality.OrthogonalLA3
open import Substrate.ShadowArchitecture.Duality.OrthogonalLB
open import Substrate.ShadowArchitecture.Duality.OrthogonalLB2
open import Substrate.ShadowArchitecture.Duality.OrthogonalLB3
open import Substrate.ShadowArchitecture.Duality.OrthogonalLC
open import Substrate.ShadowArchitecture.Duality.OrthogonalLC2
open import Substrate.ShadowArchitecture.Duality.OrthogonalLC3
open import Substrate.ShadowArchitecture.Duality.PointCover
open import Substrate.ShadowArchitecture.Weight
open import Substrate.ShadowArchitecture.SelfReference
open import Substrate.ShadowArchitecture.AxisDualLine
open import Substrate.ShadowArchitecture.Mode
open import Substrate.ShadowArchitecture.Charter
open import Substrate.ShadowArchitecture.Distinction
open import Substrate.ShadowArchitecture.Symmetry
open import Substrate.ShadowArchitecture.Loop
open import Substrate.ShadowArchitecture.Persistence