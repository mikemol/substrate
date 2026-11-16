------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipobj
--
-- Defines: v4-flip-obj
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipobj where

open import Substrate.Category.Allegory.Refinement.Preamble
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


v4-flip-obj : V4.V4Full → V4.V4Full
v4-flip-obj (V4.v4 a b) = V4.v4 a (𝟙 ⊕₂ b)
