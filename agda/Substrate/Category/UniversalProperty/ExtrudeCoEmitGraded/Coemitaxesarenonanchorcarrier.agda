------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitaxesarenonanchorcarrier
--
-- Defines: coemit-axes-are-nonanchor-carrier
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitaxesarenonanchorcarrier where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Bisim
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.Wedge
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
open import Substrate.Groups.V4.Bijection
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisfin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3reaches
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbraidtracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrung4action


-- NOTE (D-read-remaining): coemit-braid-trace-mul + coemit-rung4-action already exist above (prior turn, ~1081/1092),
-- built on the S₃-perm component. THE CATALOG'S PAYOFF is the CANONICAL V₄ above: V4Full's laws on the TRACE carrier
-- (rowSwap-invol / recip-invol / gens-commute / klein-invol / klein-is-product) — the ℤ/2×ℤ/2 Klein group the
-- reuse-index names as canonical, which the hand-rolled S₃-component laws were shadowing. The V₄ kernel of the
-- ⋊ is V4Full (4 elements: e, rowSwap, recip, klein) — matching the rung-4 wedge quot = |V₄| = 4.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- coemit-axis-reconcile (THE CORRECTION) + stab-anchor + chirality-orientation + s4iso-reuse.
-- CATALOG (context supplement, per directive): C-DCSW-axes — the FOUR axes D,C,S,W form a 4-element set S₄ acts on.
-- C-V4-Klein — V₄ = the three DOUBLE-TRANSPOSITIONS (group ELEMENTS: rowSwap, recip, klein), acting on those 4 axes.
-- C-V4-semidirect-S3 (PRIMARY) — S₄ ≅ V₄ ⋊ S₃ with S₃ = Stab(D), which permutes the THREE NON-ANCHOR axes (C,S,W).
-- Stab-S3-Iso — Stab(anchor) ≅ S₃, indexed by Fin 3 over the three non-anchor axes (4 anchor × 3 Fin 3).
--
-- >>> THE RECONCILIATION (D-verify-dont-assume-substance, corrective): my GradingAxis (3 elements, S₃-permuted) is
-- >>> the THREE NON-ANCHOR AXES (the OBJECTS Stab(D) permutes) — NOT V₄'s three involutions (which are group
-- >>> ELEMENTS acting on all FOUR axes). ADD 330-341 conflated OBJECTS (axes) with GROUP ELEMENTS (involutions).
-- >>> The S₃-action (s3-on-axis, s3-reaches) is CORRECT — it IS Stab(D) permuting the 3 non-anchor axes.
-- >>> What was WRONG: calling the 3 axes "V₄'s 3 involutions". V₄ is the KERNEL (elements), the axes are the CARRIER.
------------------------------------------------------------------------
-- (1) coemit-axis-reconcile: the 3 GradingAxis are the NON-ANCHOR axes (the S₃=Stab(D) carrier), not V₄'s elements.
--     V₄'s three non-identity ELEMENTS are rowSwap-gen, recip-gen, klein (in V4Full) — distinct from the 3 axes.
coemit-axes-are-nonanchor-carrier : GradingAxis → Fin 3      -- the 3 axes ARE the Fin 3 carrier Stab(D) permutes
coemit-axes-are-nonanchor-carrier = axis→fin
