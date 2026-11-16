------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipmorphinvol
--
-- Defines: v4-flip-morph-invol
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipmorphinvol where

open import Substrate.Category.Allegory.Refinement.Preamble
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2flipinvolutive
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipmorph
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- each is an involution: 𝟙 ⊕ (𝟙 ⊕ b) ≡ b  (f2-flip-involutive, the x⊕x=𝟘 engine).
v4-flip-morph-invol : (v : V4.V4Full) → v4-flip-morph (v4-flip-morph v) ≡ v
v4-flip-morph-invol (V4.v4 a b) = cong (λ x → V4.v4 x b) (f2-flip-involutive a)
