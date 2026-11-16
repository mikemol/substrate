------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3actcomp
--
-- Defines: s3-act-comp
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3actcomp where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisfin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Finaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


s3-act-comp : (σ τ : Fin 3 → Fin 3) (a : GradingAxis)
            → s3-on-axis σ (s3-on-axis τ a) ≡ s3-on-axis (λ x → σ (τ x)) a
s3-act-comp σ τ a = cong (λ z → fin→axis (σ z)) (fin-axis-iso (τ (axis→fin a)))
  where fin-axis-iso : (i : Fin 3) → axis→fin (fin→axis i) ≡ i
        fin-axis-iso zero             = refl
        fin-axis-iso (suc zero)       = refl
        fin-axis-iso (suc (suc zero)) = refl
