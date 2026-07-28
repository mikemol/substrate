------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisv4
--
-- Defines: axis→v4
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisv4 where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
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
open import Substrate.Algebra.F2
open import Substrate.Groups.S4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis


------------------------------------------------------------------------
-- coemit-v4-group + coemit-s4-full-group + coemit-rung4-genuine-action: closing 342's V₄ honest-partial by REUSING
-- the canonical group tree (D-graded-is-canonical, D-look-in-the-right-tree): Substrate.Groups.V4.Bijection has
-- `data V₄ : Set where e α β γ` (the 4-element Klein-four: identity e + the 3 involutions α β γ), and
-- Substrate.Groups.S4-Composed builds S₄-Group = Group-bundle (to-setoid V4.V₄-Group) S₃.S₃-Group — the genuine
-- V₄ ⋊ S₃ → S₄. coemit's GradingAxis is the 3 NON-IDENTITY involutions; the canonical V₄ supplies the missing e.
------------------------------------------------------------------------

-- (1) coemit-v4-group: coemit's 3 axes ARE the 3 non-identity elements of the canonical V₄ (the missing 4th is e).
--     The embedding closes 342's honest-partial: GradingAxis ↪ V₄ (onto {α,β,γ}), with e the identity coemit lacked.
axis→v4 : GradingAxis → V₄
axis→v4 μν-axis        = α
axis→v4 head-tail-axis = β
axis→v4 cyc-aper-axis  = γ
