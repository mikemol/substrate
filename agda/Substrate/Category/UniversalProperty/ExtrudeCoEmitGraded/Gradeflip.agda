------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Gradeflip
--
-- Defines: grade-flip
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Gradeflip where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Hodge
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (2) coemit-z-chain: GRADE-FLIP (RENAMED 345 — this is the grade involution, not the orientation). The substrate's
--     is the WitnessTower Hodge GRADE-INVOLUTION (dual-grade₃, k ↦ 3−k — NOT a Foundation parity), and it is an
--     INVOLUTION: reorienting twice returns the orientation. The simplicial ∂'s sign-change IS this grade-flip.
-- RENAMED (345): grade-flip, NOT orientation-flip. dual-grade₃ reflects Hodge GRADES (Λᵏ↔Λⁿ⁻ᵏ); the ORIENTATION is
-- chirality (which coset of A₄ in S₄). Both are involutions; they are different maps on different objects.
grade-flip : Fin 4 → Fin 4
grade-flip = dual-grade₃
