------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitagreesisbisimfwd
--
-- Defines: coemit-agrees-is-bisim-fwd
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitagreesisbisimfwd where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Final
open import Substrate.Algebra.R.Trace.Bisim
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
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Prefixseparates


------------------------------------------------------------------------
-- coemit CrossMul as GENUINE two-carrier mixing (operator: "CrossMul's purpose is to mix two carriers so their
-- terms lift into a common carrier space" — the diagonal was degenerate). The TWO carriers are coemit's TWO
-- FRAMINGS: A = the μ-framing (finite prefixes, take n — the halting/algebraic side) and B = the ν-framing
-- (RealTrace stream — the ~/coinductive side); they lift into the COMMON carrier List ℕ (finite observations),
-- and agreement there ⟺ bisimilarity. V₄'s 3 involutions = the 3 grading axes (μ/ν, head/tail, cyclic/aperiodic).
------------------------------------------------------------------------

-- (3, GENUINE) coemit-agrees-is-bisim: the two DISTINCT framings (μ = finite prefix take, ν = the stream) AGREE
-- in the common carrier List ℕ at EVERY grade ⟺ bisimilar. This is the REAL agreement (not the trivial diagonal):
-- lift-μ n r = take n r (the finite/halting framing); lift-ν = the stream via all its prefixes; agree ⟺ ~.
coemit-agrees-is-bisim-fwd : (r t : RealTrace) → ((n : ℕ) → take n t ≡ take n r) → t ~ r
coemit-agrees-is-bisim-fwd r t pre = prefix-separates t r pre
