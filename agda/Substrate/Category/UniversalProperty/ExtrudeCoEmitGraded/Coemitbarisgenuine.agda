------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbarisgenuine
--
-- Defines: coemit-bar-is-genuine
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbarisgenuine where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstepchirality
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2flip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2flipinvolutive
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- bar ON THE CHIRALITY GRADE: conjugation = flipping the step's chirality bit; involutive (f2-flip-involutive).
-- So `bar` is GENUINE (not id), V₄ = ⟨†, bar⟩ does NOT collapse to V₂. † = ~-sym (the groupoid inverse, 349).
coemit-bar-is-genuine : (n : ℕ) → f2-flip (coemit-step-chirality n) ≡ coemit-step-chirality (suc n)
coemit-bar-is-genuine n = refl
