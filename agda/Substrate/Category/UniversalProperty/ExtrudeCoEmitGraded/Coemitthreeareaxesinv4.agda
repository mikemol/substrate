------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitthreeareaxesinv4
--
-- Defines: coemit-three-are-axes-in-v4
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitthreeareaxesinv4 where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
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
open import Substrate.Axes.VOfAxis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Algebra.Wedge.Iso
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3reaches


------------------------------------------------------------------------
-- THE TWO V₄s + THE DAGGER (operator, dissolving the 343-348 thrash):
--   "The codec pair is the native DAGGER operator for the repository.
--    THREE things tied together = AXES in a V₄.  FOUR things tied together = OBJECTS in a V₄.
--    Thrashing on this point = experiencing S₄ ≅ V₄ ⋊ S₃, which has TWO V₄s sharing a C₂."
--
-- CANONICAL (Substrate.Algebra.Wedge.StarV4, verbatim):
--   • THE ARROW (V₂): the groupoid's inverse iso-sym IS THE DAGGER † — a self-inverse; its fraction-level
--     shadow is `recip` (swap).                                    [C₂ #1]
--   • THE TWISTED ARROW (the second V₂): a CONJUGATION `bar`, needing a *-involution on the carrier.  [C₂ #2]
--   • V₄ (BOTH): ⟨†, bar⟩ ≅ ℤ/2 × ℤ/2; V₄-not-dihedral BECAUSE the two involutions COMMUTE (recip-bar);
--     the fourth element † ∘ bar is the TRANSPOSE/ADJOINT.
--   • "CROSSMUL IS A KLEIN ROTATION": ⟨rowSwap, colSwap⟩ ≅ V₄; klein-rot permutes the two diagonals that
--     cross-multiplication compares (a·d vs b·c) — cross-mul's comparison is V₄-EQUIVARIANT.
-- And Substrate.WitnessTower.KleinCensus: S₄ has exactly FOUR Klein-four subgroups, each {id,a,b,ab} determined
-- by two distinct COMMUTING involutions; the V₄ object DEBUTS at rung 4.
--
-- >>> THE THRASH DISSOLVED. I oscillated (330-348) between "the 3 GradingAxis ARE V₄" and "no — the 4 axes
-- >>> D,C,S,W are V₄'s carrier". BOTH are V₄s, and that is exactly what S₄ ≅ V₄ ⋊ S₃ contains:
-- >>>   • the AXES-V₄  : three tied things (α,β,γ = the 3 double-transpositions / the 3 GradingAxis) — the NORMAL V₄
-- >>>   • the OBJECTS-V₄: four tied things (D,C,S,W = the V₄-torsor carrier, v-of-axis D = e)
-- >>> They share a C₂. In StarV4's presentation that shared C₂ is THE DAGGER † itself (the arrow's self-inverse,
-- >>> unconditional), with `bar` the twisted second V₂ that turns genuine only when the carrier has a conjugation.
-- >>> 343's "correction" was not a correction: it swapped which V₄ I was looking at. Both readings are true.
------------------------------------------------------------------------
-- the 3 GradingAxis are AXES in a V₄ (three tied things) — the normal V₄'s non-identity elements, S₃-permuted.
coemit-three-are-axes-in-v4 : (a b : GradingAxis) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ a ≡ b)
coemit-three-are-axes-in-v4 = s3-reaches       -- S₃ acts transitively on the 3 AXES (Stab(D)'s orbit)
