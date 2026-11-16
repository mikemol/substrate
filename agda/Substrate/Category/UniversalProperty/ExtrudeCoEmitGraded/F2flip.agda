------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2flip
--
-- Defines: f2-flip
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2flip where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- THE STEPWISE CONJUGATION (the *-involution the twisted arrow `bar` requires): flip the chirality bit at each
-- step. On F₂ the flip is `𝟙 +F _`, and it IS an involution: 𝟙 +F (𝟙 +F b) ≡ b (F₂: x ⊕ x = 𝟘).
f2-flip : F₂ → F₂
f2-flip b = 𝟙 +F b
