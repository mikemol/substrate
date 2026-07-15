------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.BabyMonster
--
-- The Baby Monster group B, order 2^41 · 3^13 · 5^6 · 7^2 · 11 · 13 ·
-- 17 · 19 · 23 · 31 · 47 ≈ 4.15 × 10^33. The second-largest sporadic
-- simple group, defined as the centralizer of a 2A-class involution
-- in the Monster, then quotient by the central ⟨z⟩.
--
-- V2 of the 20-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- The substrate's first centralizer-descent instance from T8 Monster.
--
-- Structural identification (per Griess 1982; Conway-Norton 1979):
--
--   2·B = C_M(z)   for z a 2A-class involution
--   B   = C_M(z) / ⟨z⟩
--
-- where 2·B is a non-split central extension of B by ⟨z⟩.
--
-- BabyMonster has 184 conjugacy classes (ATLAS-cited count).
--
-- Module-parametric over BabyMonster's abstract data, analogous to
-- T8 Monster.AsCoalgebra. The centralizer-descent identification
-- with Monster lives in commentary (= structural claim cited from
-- external mathematical content; CentralizerDescent V1 primitive
-- provides the substrate-side type structure but doesn't enforce
-- this identification without an external CFSG citation).
--
-- Per [[expose-generator-not-orbit]] at extreme scale: 184 classes
-- (vs ~10^33 elements). Per [[coalgebraic-not-consumer-driven]]:
-- ConjugationCoalgebra IS the substrate's natural representation;
-- BabyMonster fits cleanly via T3's primitive interface.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)

open import Substrate.Category.ConjugationCoalgebra
  using (ConjugationCoalgebra; mkConjugationCoalgebra)

module Substrate.Algebra.Sporadic.BabyMonster
  -- The abstract BabyMonster carrier.
  (B : Set)
  -- Group operations on B.
  (_·B_ : B → B → B)
  (εB : B)
  (_⁻¹B : B → B)
  -- The 184 conjugacy classes (ATLAS-cited count).
  (rep-B : Fin 184 → B)
  (in-class-B : Fin 184 → B → Set)
  -- Class structure axioms.
  (in-class-rep-B : (c : Fin 184) → in-class-B c (rep-B c))
  (conjugation-respects-class-B :
    (g : B) (c : Fin 184) (h : B) →
    in-class-B c h →
    in-class-B c ((g ·B h) ·B (g ⁻¹B)))
  where

------------------------------------------------------------------------
-- 1. The BabyMonster as a ConjugationCoalgebra.
------------------------------------------------------------------------

BabyMonster-ConjugationCoalgebra : ConjugationCoalgebra B _·B_ εB _⁻¹B (Fin 184) rep-B in-class-B
BabyMonster-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep-B conjugation-respects-class-B

------------------------------------------------------------------------
-- 2. Number of conjugacy classes (= 184; ATLAS-cited).
------------------------------------------------------------------------

BabyMonster-class-count : ℕ
BabyMonster-class-count = 184

------------------------------------------------------------------------
-- 3. Capstone — BabyMonster lives in the substrate.
--
-- V2 of the 20-slice arc. Second sporadic group as a substrate-
-- internal ConjugationCoalgebra (after T8 Monster).
--
-- Structural identification (cited; not internally proven):
--   B ≅ C_M(z) / ⟨z⟩
-- where z is any 2A-class involution in M.
--
-- This module bridges external mathematical content into the
-- substrate via the standard ConjugationCoalgebra interface.
-- Concrete usage requires consumer modules to supply the 7 abstract
-- parameters citing CFSG + ATLAS.
--
-- Next: V3 (Conway groups via 2B-class descent), V4 (Mathieu+Fischer),
-- V5 (HappyFamily catalog + capstone).
------------------------------------------------------------------------
