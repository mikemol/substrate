------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4mulisf2add
--
-- Defines: coemit-v4-mul-is-f2-add
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4mulisf2add where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4


-- and V₄'s "multiplication" is componentwise F₂ ADDITION — the codec is DEFINITIONAL here (no exp/log needed):

coemit-v4-mul-is-f2-add : (a b c d : F₂) → V4._·_ (V4.v4 a b) (V4.v4 c d) ≡ V4.v4 (a ⊕₂ c) (b ⊕₂ d)
coemit-v4-mul-is-f2-add a b c d = refl
