------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstabanchor
--
-- Defines: coemit-stab-anchor
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstabanchor where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3reaches
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- (2) coemit-stab-anchor: S₃ = Stab(D) acts on the 3 NON-ANCHOR axes. My s3-on-axis IS this action (now correctly
--     named): the anchor D is fixed; C,S,W (the GradingAxis) are permuted. s3-reaches = Stab(D)'s transitivity.
coemit-stab-anchor : (a b : GradingAxis) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ a ≡ b)
coemit-stab-anchor = s3-reaches      -- Stab(D) is transitive on the 3 non-anchor axes (the anchor is fixed)
