------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4fixunit
--
-- Defines: v4-fix→unit
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4fixunit where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.R.Trace.Bisim.Refl
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon3
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2cancel
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- V₄'s cancellation: g · x ≡ x ⇒ g ≡ e (componentwise F₂ cancellation).
v4-fix→unit : (g x : V4.V4Full) → V4._·_ g x ≡ x → g ≡ V4.e
v4-fix→unit (V4.v4 a b) (V4.v4 c d) eq =
  cong₂ V4.v4 (f2-cancel a c (cong morph-of eq)) (f2-cancel b d (cong obj-of eq))
  where morph-of : V4.V4Full → F₂
        morph-of (V4.v4 m _) = m
        obj-of : V4.V4Full → F₂
        obj-of (V4.v4 _ o) = o
