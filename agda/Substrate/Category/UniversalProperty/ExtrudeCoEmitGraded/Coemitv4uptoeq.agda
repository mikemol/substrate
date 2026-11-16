------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4uptoeq
--
-- Defines: coemit-v4-upto-eq
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4uptoeq where

open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon3
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Axes.Axis

open import Substrate.Groups.Symmetric.Eq Axis
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipmorph
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipobj
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipmorphinvol
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipobjinvol
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipscommute
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4

-- INSTANCE 1 (≈ := ≡): V4Full, the F₂×F₂ coords — recovering the canonical Lawvere atom's content exactly.
coemit-v4-upto-eq : CommutingInvolutionsUpTo V4.V4Full _≡_
coemit-v4-upto-eq = record
  { δ₁ = v4-flip-morph ; δ₂ = v4-flip-obj
  ; δ₁-inv = v4-flip-morph-invol ; δ₂-inv = v4-flip-obj-invol ; commute = v4-flips-commute }
