------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Phiobsnonshrinkbwd
--
-- Defines: phi-obs-nonshrink-bwd
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Phiobsnonshrinkbwd where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Iterate
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.SqsubF
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.Iterate
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.SqsubF
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.R
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrefinement
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


phi-obs-nonshrink-bwd : (n : ℕ) → R⁰ ⊑ᶠ iterate coemit-refinement n R⁰
phi-obs-nonshrink-bwd zero    a p = p
phi-obs-nonshrink-bwd (suc n) zero    p = phi-obs-nonshrink-bwd n zero p
phi-obs-nonshrink-bwd (suc n) (suc a) p = phi-obs-nonshrink-bwd n a p
