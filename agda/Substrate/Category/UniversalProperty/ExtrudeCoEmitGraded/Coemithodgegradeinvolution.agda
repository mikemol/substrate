------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemithodgegradeinvolution
--
-- Defines: coemit-hodge-grade-involution
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemithodgegradeinvolution where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Hodge
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- (3) coemit-hodge-axis: Hodge's dual-grade₃ (Λ⁰↔Λ³, Λ¹↔Λ² — the grade involution) IS the μν-axis flip. The
--     grade-duality (Hodge ★) riding the rung-3→4 seam = the μ↔ν axis reflection (one of V₄'s 3 involutions).
------------------------------------------------------------------------

-- the Hodge grade-involution is an involution (Λ⁰↔Λ³, Λ¹↔Λ²), matching axis-flip's flip²=id (the μν-axis).
-- RENAMED (345 retraction discharged): this is the Hodge GRADE involution (Λᵏ↔Λⁿ⁻ᵏ), NOT the μν/orientation flip.
-- The canonical orientation is chirality (S₄/A₄ parity) — see coemit-orientation-of. The FACT stands; the name was wrong.
coemit-hodge-grade-involution : (i : Fin 4) → dual-grade₃ (dual-grade₃ i) ≡ i
coemit-hodge-grade-involution = dual-grade₃-involution
  where open import Substrate.Foundation.Fin.Fin
