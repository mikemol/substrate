------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.Conway
--
-- The three Conway sporadic groups: Co₁, Co₂, Co₃. Each as a
-- parametric ConjugationCoalgebra. Together they form a descending
-- chain of subquotients arising from the Monster's 2B-class
-- centralizer (= 2^(1+24).Co₁, whose Co₁ quotient gives Co₁ directly).
--
-- V3 of the 20-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- Adds 3 sporadic groups to the substrate (after T8 Monster, V2
-- BabyMonster).
--
-- Group structure (ATLAS-cited):
--
--   Co₁: order 2²¹·3⁹·5⁴·7²·11·13·23 ≈ 4.16 × 10^18; 101 conjugacy classes
--   Co₂: order 2¹⁸·3⁶·5³·7·11·23     ≈ 4.23 × 10^13;  60 conjugacy classes
--   Co₃: order 2¹⁰·3⁷·5³·7·11·23     ≈ 4.96 × 10^11;  42 conjugacy classes
--
-- All three arise from the Leech lattice's automorphism group Co₀
-- = Aut(Λ) of order 2|Co₁|, with Co₁ = Co₀ / {±1}. Co₂ and Co₃ are
-- stabilisers of specific Leech-lattice vectors of norm 4 and 6.
--
-- Per [[expose-generator-not-orbit]]: each Conway group has ~10²
-- conjugacy classes representing 10^11-18 elements — substrate
-- compression: 9-16 orders of magnitude.
--
-- This module provides three nested parametric submodules
-- (Co1, Co2, Co3), each producing a ConjugationCoalgebra value from
-- ATLAS-cited data parameters.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Sporadic.Conway where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)

open import Substrate.Category.ConjugationCoalgebra
  using (ConjugationCoalgebra; mkConjugationCoalgebra)

------------------------------------------------------------------------
-- 1. Co₁ — the largest Conway group.
------------------------------------------------------------------------

module Co1
  (Co1-G : Set)
  (_·_ : Co1-G → Co1-G → Co1-G)
  (ε : Co1-G)
  (_⁻¹ : Co1-G → Co1-G)
  (rep : Fin 101 → Co1-G)
  (in-class : Fin 101 → Co1-G → Set)
  (in-class-rep : (c : Fin 101) → in-class c (rep c))
  (conj-resp-class :
    (g : Co1-G) (c : Fin 101) (h : Co1-G) →
    in-class c h →
    in-class c ((g · h) · (g ⁻¹)))
  where

  Co1-ConjugationCoalgebra : ConjugationCoalgebra
  Co1-ConjugationCoalgebra = mkConjugationCoalgebra
    Co1-G _·_ ε _⁻¹
    (Fin 101) rep in-class in-class-rep conj-resp-class

  Co1-class-count : ℕ
  Co1-class-count = 101

------------------------------------------------------------------------
-- 2. Co₂.
------------------------------------------------------------------------

module Co2
  (Co2-G : Set)
  (_·_ : Co2-G → Co2-G → Co2-G)
  (ε : Co2-G)
  (_⁻¹ : Co2-G → Co2-G)
  (rep : Fin 60 → Co2-G)
  (in-class : Fin 60 → Co2-G → Set)
  (in-class-rep : (c : Fin 60) → in-class c (rep c))
  (conj-resp-class :
    (g : Co2-G) (c : Fin 60) (h : Co2-G) →
    in-class c h →
    in-class c ((g · h) · (g ⁻¹)))
  where

  Co2-ConjugationCoalgebra : ConjugationCoalgebra
  Co2-ConjugationCoalgebra = mkConjugationCoalgebra
    Co2-G _·_ ε _⁻¹
    (Fin 60) rep in-class in-class-rep conj-resp-class

  Co2-class-count : ℕ
  Co2-class-count = 60

------------------------------------------------------------------------
-- 3. Co₃.
------------------------------------------------------------------------

module Co3
  (Co3-G : Set)
  (_·_ : Co3-G → Co3-G → Co3-G)
  (ε : Co3-G)
  (_⁻¹ : Co3-G → Co3-G)
  (rep : Fin 42 → Co3-G)
  (in-class : Fin 42 → Co3-G → Set)
  (in-class-rep : (c : Fin 42) → in-class c (rep c))
  (conj-resp-class :
    (g : Co3-G) (c : Fin 42) (h : Co3-G) →
    in-class c h →
    in-class c ((g · h) · (g ⁻¹)))
  where

  Co3-ConjugationCoalgebra : ConjugationCoalgebra
  Co3-ConjugationCoalgebra = mkConjugationCoalgebra
    Co3-G _·_ ε _⁻¹
    (Fin 42) rep in-class in-class-rep conj-resp-class

  Co3-class-count : ℕ
  Co3-class-count = 42

------------------------------------------------------------------------
-- 4. Capstone — three Conway groups in substrate.
--
-- V3 of the 20-slice arc. With V3 + V2 + T8, the substrate hosts
-- 5 sporadic groups (Monster, BabyMonster, Co₁, Co₂, Co₃) — about
-- a quarter of the 20-member Happy Family.
--
-- Structural relationships (cited):
--   * Co₀ = Aut(Λ) where Λ = Leech lattice; Co₁ = Co₀ / {±1}
--   * 2^(1+24).Co₁ = C_M(z) for z a 2B-class Monster involution
--   * Co₂ = stabiliser of a norm-4 Leech vector in Co₀
--   * Co₃ = stabiliser of a norm-6 Leech vector in Co₀
--
-- Next: V4 (Mathieu groups M₁₁-M₂₄ + Fischer groups Fi₂₂-Fi₂₄').
------------------------------------------------------------------------
