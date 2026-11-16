------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrung4orbit
--
-- Defines: coemit-rung4-orbit
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrung4orbit where

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


-- the rung-4 action's carrier is the V₄ coset space (4 = |V₄|): the S₃-orbit on the 3 axes lives INSIDE this rung-4
-- structure (the 3 involutions are 3 of the 4 cosets; s3-reaches is the S₃-action on them, at the rung where V₄ debuts).
coemit-rung4-orbit : (a b : GradingAxis) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ a ≡ b)
coemit-rung4-orbit = s3-reaches
