------------------------------------------------------------------------
-- Substrate.Category.Allegory.RefinementReconstruct
--
-- SYNTHESIZED by jea/metalanguage/synth_agda_prototype.py (⟡pipeline-driver,
-- `reconstruct` class) — the Set₀ reconstruction of `Substrate.Category.Allegory
-- .Refinement` (ALG-7 — the monotone Φ-operator on FIBER FAMILIES; NB this is NOT the
-- unrelated `Substrate.Category.UniversalProperty.Refinement`, which is cover-refinement).
-- Substrate-only imports (no stdlib). It is Set₁, and we reconstruct it as a TRUNCATION
-- of its graded, grade-EXPOSED form. The shape was located
-- MECHANICALLY: numpy verified the Φ-chain C n = Φⁿ R⁰ is a DESCENDING graded
-- family (Rⁿ⁺¹ ⊑ Rⁿ; the grade IS the chain, over all subsets of Fin 4); jea_pysim
-- located the carrier-hole C : ℕ→Set + the graded field (n)→C(suc n)→C n.
--
-- Refinement's Set₁ is the GRADE-COLLAPSE: it holds Φ : Fam A → Fam A (Fam A =
-- A → Set : Set₁) instead of the graded C : ℕ→Set. GRefinement EXPOSES the grade
-- (C a MODULE PARAM ⇒ the record lands at `: Set`, the paydown), and `reify` shows
-- Refinement REIFIES to it (the 'build MORE' — the constructive graded chain). The
-- RESIDUE is the grade n itself: recovering the ABSTRACT Φ-operator back from the
-- graded form re-quantifies over Fam (Set₁) — that Set₁ is exactly the grade the
-- truncation drops. This closes the arc's 'IDENTIFIED NOT YET PROVEN' ALG-7 chain
-- deferral to the reification degree. Zero postulates, zero holes, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.RefinementReconstruct where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Category.Allegory.Refinement
  using (Refinement; Fam; iterate; _⊑ᶠ_)
open Refinement using (Φ; mono)   -- Φ/mono are record field projections

-- THE RICH Set₀ RECONSTRUCTION: the grade EXPOSED as a graded family. C : ℕ → Set
-- is a MODULE PARAMETER (not a held field), so the bundle lands at `: Set` — NOT
-- Set₁. That green compile at `: Set` IS the Set₁ paydown.
module _ (C : ℕ → Set) where
  record GRefinement : Set where
    field
      step : (n : ℕ) → C (suc n) → C n

-- the descent chain (Refinement.mono + a pre-fixed-point Φ R⁰ ⊑ R⁰): Rⁿ⁺¹ ⊑ᶠ Rⁿ.
descend : {A : Set} (r : Refinement A) (R⁰ : Fam A) →
          Φ r R⁰ ⊑ᶠ R⁰ → (n : ℕ) → iterate r (suc n) R⁰ ⊑ᶠ iterate r n R⁰
descend r R⁰ pre zero    = pre
descend r R⁰ pre (suc n) = mono r (descend r R⁰ pre n)

-- REIFY (the 'build MORE'): Refinement's abstract Φ-operator, at a pre-fixed-point
-- R⁰ and a point a, reifies to the graded, grade-exposed form. The graded step at
-- n is the descent Rⁿ⁺¹ ⊑ Rⁿ read at a.
reify : {A : Set} (r : Refinement A) (R⁰ : Fam A) →
        Φ r R⁰ ⊑ᶠ R⁰ → (a : A) → GRefinement (λ n → iterate r n R⁰ a)
reify r R⁰ pre a = record { step = λ n → descend r R⁰ pre n a }
