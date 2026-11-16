------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitgradeinvolutionnotorientation
--
-- Defines: coemit-grade-involution-not-orientation
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitgradeinvolutionnotorientation where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Hodge
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- 334's dual-grade₃ is RETAINED under its correct name: a GRADE involution (Λᵏ↔Λⁿ⁻ᵏ), NOT the orientation.
-- The two are distinct: orientation ∈ Chirality (group cosets); dual-grade₃ : Fin 4 → Fin 4 (Hodge grades).
coemit-grade-involution-not-orientation : (i : Fin 4) → dual-grade₃ (dual-grade₃ i) ≡ i
coemit-grade-involution-not-orientation = dual-grade₃-involution
