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
--   Duality         — `normal-vector : Line → Point` and its inverse,
--                     orthogonality proofs.
--   Weight          — Hamming weight + three-orbit partition.
--   SelfReference   — ★ L₆-normal=110, L₇-normal=111, the wt-3 fixed
--                     pair non-incidence.
--   AxisDualLine    — `axis-dual : Axis → Line`.
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

open import Substrate.ShadowArchitecture.FanoLabeling   public
open import Substrate.ShadowArchitecture.Duality        public
open import Substrate.ShadowArchitecture.Weight         public
open import Substrate.ShadowArchitecture.SelfReference  public
open import Substrate.ShadowArchitecture.AxisDualLine   public
open import Substrate.ShadowArchitecture.Mode           public
open import Substrate.ShadowArchitecture.Charter        public
open import Substrate.ShadowArchitecture.Distinction    public
open import Substrate.ShadowArchitecture.Symmetry       public
open import Substrate.ShadowArchitecture.Loop           public
open import Substrate.ShadowArchitecture.Persistence    public
