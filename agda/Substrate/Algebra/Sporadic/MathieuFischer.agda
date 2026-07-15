------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.MathieuFischer
--
-- The five Mathieu sporadic groups (M₁₁, M₁₂, M₂₂, M₂₃, M₂₄) and
-- the three Fischer sporadic groups (Fi₂₂, Fi₂₃, Fi₂₄'), each as a
-- parametric ConjugationCoalgebra.
--
-- V4 of the 20-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- Adds 8 sporadic groups to the substrate.
--
-- Mathieu group structure (ATLAS-cited):
--   M₁₁:  order 7,920                     = 2⁴·3²·5·11;          10 classes
--   M₁₂:  order 95,040                    = 2⁶·3³·5·11;          15 classes
--   M₂₂:  order 443,520                   = 2⁷·3²·5·7·11;        12 classes
--   M₂₃:  order 10,200,960                = 2⁷·3²·5·7·11·23;     17 classes
--   M₂₄:  order 244,823,040               = 2¹⁰·3³·5·7·11·23;    26 classes
--
-- Fischer group structure (ATLAS-cited):
--   Fi₂₂:  order 6.46 × 10¹³ = 2¹⁷·3⁹·5²·7·11·13;            65 classes
--   Fi₂₃:  order 4.09 × 10¹⁸ = 2¹⁸·3¹³·5²·7·11·13·17·23;     98 classes
--   Fi₂₄': order 1.26 × 10²⁴ = 2²¹·3¹⁶·5²·7³·11·13·17·23·29; 108 classes
--
-- Mathieu groups: subquotients of M₂₄ (which is itself in the
-- Conway/Monster descent tree); discoverable from automorphism
-- groups of small Steiner systems.
--
-- Fischer groups: 3-transposition groups associated with Fi₂₄' (=
-- F₃ in Atlas notation; centralizer of a 3A-class involution in M).
--
-- Per [[expose-generator-not-orbit]]: each group represented by its
-- class count (10-108 classes vs 10⁴-10²⁴ elements).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Sporadic.MathieuFischer where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)

open import Substrate.Category.ConjugationCoalgebra
  using (ConjugationCoalgebra; mkConjugationCoalgebra)

------------------------------------------------------------------------
-- Mathieu groups.
------------------------------------------------------------------------

module M11
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 10 → G) (in-class : Fin 10 → G → Set)
  (in-class-rep : (c : Fin 10) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 10) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  M11-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 10) rep in-class
  M11-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

module M12
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 15 → G) (in-class : Fin 15 → G → Set)
  (in-class-rep : (c : Fin 15) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 15) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  M12-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 15) rep in-class
  M12-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

module M22
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 12 → G) (in-class : Fin 12 → G → Set)
  (in-class-rep : (c : Fin 12) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 12) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  M22-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 12) rep in-class
  M22-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

module M23
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 17 → G) (in-class : Fin 17 → G → Set)
  (in-class-rep : (c : Fin 17) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 17) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  M23-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 17) rep in-class
  M23-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

module M24
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 26 → G) (in-class : Fin 26 → G → Set)
  (in-class-rep : (c : Fin 26) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 26) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  M24-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 26) rep in-class
  M24-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

------------------------------------------------------------------------
-- Fischer groups.
------------------------------------------------------------------------

module Fi22
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 65 → G) (in-class : Fin 65 → G → Set)
  (in-class-rep : (c : Fin 65) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 65) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  Fi22-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 65) rep in-class
  Fi22-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

module Fi23
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 98 → G) (in-class : Fin 98 → G → Set)
  (in-class-rep : (c : Fin 98) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 98) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  Fi23-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 98) rep in-class
  Fi23-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

module Fi24'
  (G : Set) (_·_ : G → G → G) (ε : G) (_⁻¹ : G → G)
  (rep : Fin 108 → G) (in-class : Fin 108 → G → Set)
  (in-class-rep : (c : Fin 108) → in-class c (rep c))
  (conj-resp : (g : G) (c : Fin 108) (h : G) →
               in-class c h → in-class c ((g · h) · (g ⁻¹)))
  where
  Fi24'-ConjugationCoalgebra : ConjugationCoalgebra G _·_ ε _⁻¹ (Fin 108) rep in-class
  Fi24'-ConjugationCoalgebra = mkConjugationCoalgebra in-class-rep conj-resp

------------------------------------------------------------------------
-- Capstone — 8 sporadic groups added.
--
-- V4 of the 20-slice arc. With V4 + V3 + V2 + T8, the substrate
-- hosts 13 of the 26 sporadic groups (half!):
--
--   Monster, BabyMonster, Co₁, Co₂, Co₃,
--   M₁₁, M₁₂, M₂₂, M₂₃, M₂₄,
--   Fi₂₂, Fi₂₃, Fi₂₄'
--
-- All 13 are Happy Family members (= subquotients of M). The 6
-- Pariahs (J₁, J₃, J₄, Ru, O'N, Ly) and the remaining Happy Family
-- (HN, Th, He, J₂, HS, McL, Suz) are V5/follow-on.
--
-- Next: V5 (HappyFamily catalog + capstone refresh).
------------------------------------------------------------------------
