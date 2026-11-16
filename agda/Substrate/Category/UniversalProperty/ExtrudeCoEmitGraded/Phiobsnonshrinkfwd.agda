------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Phiobsnonshrinkfwd
--
-- Defines: phi-obs-nonshrink-fwd
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Phiobsnonshrinkfwd where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Iterate
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.SqsubF
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.Iterate
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.SqsubF
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Takevec
open import Substrate.Category.Allegory.Refinement.Present
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.R
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Obs
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrefinement
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Prefixseparates
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- coemit-phi-obs-gfp: the two Φ's reconciled (D-two-phi-distinct, 318). The fiber refinement Φ-obs is NON-SHRINKING
-- (Refinement's note: vec/tower-graded instances are fixed/non-shrinking): iterate n R⁰ = R⁰ (Present preserved at
-- every grade). So its gfp νΦ-obs = R⁰, DEGENERATE — it carries no limit content. The SUBSTANTIVE limit is at the
-- CARRIER Φ_T: the growing Vec-prefix (take-vec, C n) and its determination of the trace (prefix-separates). So the
-- grading-Φ (Φ-obs, bookkeeping) and the carrier-Φ (Φ_T, the real limit) are DISTINCT — the bridge is prefix-separates, not the fiber gfp.
------------------------------------------------------------------------
-- Φ-obs is non-shrinking: iterate n R⁰ ⊑ᶠ R⁰ (and R⁰ ⊑ᶠ iterate n R⁰) — the chain is constant, gfp = R⁰.
phi-obs-nonshrink-fwd : (n : ℕ) → iterate coemit-refinement n R⁰ ⊑ᶠ R⁰
phi-obs-nonshrink-fwd n a _ = present   -- R⁰ a = Present, always inhabited (target is Present)
