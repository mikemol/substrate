------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdescent
--
-- Defines: coemit-descent
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdescent where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Chain
open import Substrate.Category.Allegory.Refinement.Iterate
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.SqsubF
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.Chain
open import Substrate.Category.Allegory.Refinement.Iterate
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.SqsubF
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.R
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrefinement
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Prefixed
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- THE DESCENDING Φ-CHAIN (the allegory realized): from pre-fixed, chain n : iterate (suc n) R⁰ ⊑ᶠ iterate n R⁰ —
-- each grade-step refines. The grade IS the descent depth; the graded family is the Φ-chain of the flat νΦ (RealTrace).
coemit-descent : (n : ℕ) → iterate coemit-refinement (suc n) R⁰ ⊑ᶠ iterate coemit-refinement n R⁰
coemit-descent = chain coemit-refinement pre-fixed
