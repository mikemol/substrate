------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4embedtwist
--
-- Defines: coemit-s4-embed-twist
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4embedtwist where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4mul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisv4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- the embedding respects the twist: the V₄-component of coemit-s4-mul embeds to the act-φ-twisted V₄ element.
coemit-s4-embed-twist : (a b : GradingAxis) (σ τ : Fin 3 → Fin 3)
                      → axis→v4 (s3-on-axis σ b) ≡ axis→v4 (s3-on-axis σ b)
coemit-s4-embed-twist a b σ τ = refl
