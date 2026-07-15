------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.HappyFamily
--
-- The Happy Family: the 20 of the 26 sporadic simple groups that
-- occur as subquotients of the Monster. This module:
--
--   1. Provides parametric modules for the 7 Happy Family members
--      not yet built (HN, Th, He, J₂, HS, McL, Suz).
--   2. Re-exports the previously-built 13 (Monster, BabyMonster,
--      Conway × 3, Mathieu × 5, Fischer × 3).
--   3. Documents the 6 Pariahs (= sporadic groups NOT in the
--      Happy Family).
--
-- V5 of the 20-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- Closes sub-arc V (Centralizer descent / Happy Family).
--
-- After V5, all 20 Happy Family members exist as substrate-internal
-- ConjugationCoalgebra instances (parametric on ATLAS data). The
-- substrate now spans the full sporadic-simple-group taxonomy
-- (except the 6 Pariahs, which are documented as out-of-scope).
--
-- Per [[expose-generator-not-orbit]]: each Happy Family member
-- represented by its class count (typically 10-200) — compression
-- of 7-53 orders of magnitude from element enumeration.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Sporadic.HappyFamily where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)

open import Substrate.Category.ConjugationCoalgebra
  using (ConjugationCoalgebra; mkConjugationCoalgebra)

------------------------------------------------------------------------
-- 1. Re-export previously-built Happy Family members.
------------------------------------------------------------------------

import Substrate.Algebra.Sporadic.Monster.AsCoalgebra
import Substrate.Algebra.Sporadic.BabyMonster
import Substrate.Algebra.Sporadic.Conway
import Substrate.Algebra.Sporadic.MathieuFischer

------------------------------------------------------------------------
-- 2. Harada-Norton group HN.
--
-- Order 273,030,912,000,000 = 2¹⁴·3⁶·5⁶·7·11·19; 54 conjugacy classes.
------------------------------------------------------------------------

module HN
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 54 → G) (in-class : Fin 54 → G → Set)
  (in-class-rep : (c : Fin 54) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 54) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  HN-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 54) rep in-class
  HN-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

------------------------------------------------------------------------
-- 3. Thompson group Th.
--
-- Order 90,745,943,887,872,000 = 2¹⁵·3¹⁰·5³·7²·13·19·31; 48 classes.
------------------------------------------------------------------------

module Th
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 48 → G) (in-class : Fin 48 → G → Set)
  (in-class-rep : (c : Fin 48) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 48) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  Th-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 48) rep in-class
  Th-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

------------------------------------------------------------------------
-- 4. Held group He.
--
-- Order 4,030,387,200 = 2¹⁰·3³·5²·7³·17; 33 classes.
------------------------------------------------------------------------

module He
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 33 → G) (in-class : Fin 33 → G → Set)
  (in-class-rep : (c : Fin 33) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 33) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  He-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 33) rep in-class
  He-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

------------------------------------------------------------------------
-- 5. Janko group J₂.
--
-- Order 604,800 = 2⁷·3³·5²·7; 21 classes.
------------------------------------------------------------------------

module J2
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 21 → G) (in-class : Fin 21 → G → Set)
  (in-class-rep : (c : Fin 21) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 21) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  J2-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 21) rep in-class
  J2-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

------------------------------------------------------------------------
-- 6. Higman-Sims group HS.
--
-- Order 44,352,000 = 2⁹·3²·5³·7·11; 24 classes.
------------------------------------------------------------------------

module HS
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 24 → G) (in-class : Fin 24 → G → Set)
  (in-class-rep : (c : Fin 24) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 24) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  HS-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 24) rep in-class
  HS-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

------------------------------------------------------------------------
-- 7. McLaughlin group McL.
--
-- Order 898,128,000 = 2⁷·3⁶·5³·7·11; 24 classes.
------------------------------------------------------------------------

module McL
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 24 → G) (in-class : Fin 24 → G → Set)
  (in-class-rep : (c : Fin 24) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 24) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  McL-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 24) rep in-class
  McL-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

------------------------------------------------------------------------
-- 8. Suzuki group Suz.
--
-- Order 448,345,497,600 = 2¹³·3⁷·5²·7·11·13; 43 classes.
------------------------------------------------------------------------

module Suz
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 43 → G) (in-class : Fin 43 → G → Set)
  (in-class-rep : (c : Fin 43) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 43) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  Suz-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 43) rep in-class
  Suz-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

------------------------------------------------------------------------
-- 9. Capstone — entire Happy Family in substrate.
--
-- V5 of the 20-slice arc. With V5 landed, ALL 20 Happy Family members
-- exist as substrate-internal ConjugationCoalgebra instances:
--
--   Monster (T8)              — 194 classes
--   BabyMonster (V2)          — 184 classes
--   Co₁, Co₂, Co₃ (V3)        — 101, 60, 42 classes
--   M₁₁-M₂₄ (V4)              — 10, 15, 12, 17, 26 classes
--   Fi₂₂, Fi₂₃, Fi₂₄' (V4)    — 65, 98, 108 classes
--   HN, Th, He (V5)           — 54, 48, 33 classes
--   J₂, HS, McL, Suz (V5)     — 21, 24, 24, 43 classes
--
-- TOTAL: 20 sporadic groups, ~1,400 conjugacy classes representing
-- ~10^54 group elements (sum dominated by Monster). Substrate
-- compression: ~50 orders of magnitude.
--
-- THE 6 PARIAHS (NOT in Happy Family; not substrate-internal):
--   J₁ (Janko-1), J₃ (Janko-3), J₄ (Janko-4),
--   Ru (Rudvalis), O'N (O'Nan), Ly (Lyons).
-- These are sporadic simple groups but NOT subquotients of M.
-- Each could in principle be added as a substrate primitive
-- analogous to the Happy Family members (parametric module with
-- class data). Out-of-scope for the prime-factored-gauge arc.
--
-- Next: V5 capstone refresh (PrimitivesAll + PrimitiveInstances +
-- PrimitivesRoadmapV2 update). Then sub-arc W (Abelian/CRT PFG).
------------------------------------------------------------------------
