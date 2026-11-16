------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Prefixed
--
-- Defines: pre-fixed
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Prefixed where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.SqsubF
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.SqsubF
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.Allegory.Refinement.Present
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.R
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Obs
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the pre-fixed-point Φ R⁰ ⊑ᶠ R⁰ (both constantly Present) → the DESCENDING chain (grade = observation depth).
pre-fixed : Φ-obs R⁰ ⊑ᶠ R⁰
pre-fixed zero    p = p
pre-fixed (suc n) p = p
