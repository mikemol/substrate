------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4twistisactphi
--
-- Defines: coemit-s4-twist-is-actphi
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4twistisactphi where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4mul
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- the twist IS the semidirect structure: the V₄-component of the product is the act-φ twist (s3-on-axis), witnessed.
coemit-s4-twist-is-actphi : (a b : GradingAxis) (σ τ : Fin 3 → Fin 3)
                          → Σ.proj₁ (coemit-s4-mul (a , σ) (b , τ)) ≡ s3-on-axis σ b
coemit-s4-twist-is-actphi a b σ τ = refl
  where open import Substrate.Foundation.Product using (module Σ)
