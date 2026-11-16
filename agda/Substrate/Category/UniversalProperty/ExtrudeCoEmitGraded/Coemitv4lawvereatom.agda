------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4lawvereatom
--
-- Defines: coemit-v4-lawvere-atom
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4lawvereatom where

open import Substrate.Category.Allegory.Refinement.Preamble
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


-- coemit's V₄ AS the canonical Lawvere atom (carrier-generic, in Set — no Set₁ bump).
coemit-v4-lawvere-atom : CommutingInvolutions V4.V4Full
coemit-v4-lawvere-atom = record
  { δ₁      = v4-flip-morph
  ; δ₂      = v4-flip-obj
  ; δ₁-inv  = v4-flip-morph-invol
  ; δ₂-inv  = v4-flip-obj-invol
  ; commute = v4-flips-commute
  }
