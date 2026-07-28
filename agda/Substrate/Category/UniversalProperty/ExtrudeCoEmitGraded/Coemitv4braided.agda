------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4braided
--
-- Defines: coemit-v4-braided
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4braided where

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
open import Substrate.Groups.V4.Bijection
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisflip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisflipinvolution


------------------------------------------------------------------------
-- THE BRAIDING CHAIN (operator: braid just S₃, all of V₄, or the full S₃/V₄/S₄ chain?). D-model-the-coset: the
-- either/or DISSOLVES — the invariant is S₄ = V₄ ⋊ S₃ (the full chain), because the braiding IS the ⋊. From
-- SemidirectProduct: (n₁,h₁) ·⋊ (n₂,h₂) = (n₁ ·N (act φ h₁ n₂)) , (h₁ ·H h₂) — the V₄ component (n) is combined
-- THROUGH act φ h₁ (S₃ acting on V₄); the S₃ component (h) composes directly. So braiding S₃ alone [339] misses
-- V₄'s involutions; braiding V₄ alone misses S₃'s permutation; the ⋊ (the act-φ twist) IS the braiding that glues them.
------------------------------------------------------------------------
-- the V₄ leg: each axis is an involution (axis-flip, order 2). The 3 involutions ARE V₄'s 3 non-identity elements.
-- Braided through the coinduction: the involution is available at every depth (V₄'s ℤ/2×ℤ/2, the axes themselves).
coemit-v4-braided : (a : GradingAxis) (r : RealTrace) (n : ℕ) → axis-flip (axis-flip a) ≡ a
coemit-v4-braided a r n = axis-flip-involution a
