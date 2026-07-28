------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Phiobsnonshrinkfwd
--
-- Defines: phi-obs-nonshrink-fwd
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Phiobsnonshrinkfwd where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Category.Allegory.Refinement
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Takevec
open import Substrate.Category.Allegory.Refinement.Present
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.R
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Obs
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrefinement
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Prefixseparates


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
