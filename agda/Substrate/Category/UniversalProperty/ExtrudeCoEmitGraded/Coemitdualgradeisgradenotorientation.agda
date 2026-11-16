------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdualgradeisgradenotorientation
--
-- Defines: coemit-dual-grade-is-grade-not-orientation
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdualgradeisgradenotorientation where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Hodge
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


coemit-dual-grade-is-grade-not-orientation : (i : Fin 4) → dual-grade₃ (dual-grade₃ i) ≡ i   -- an involution, on GRADES
coemit-dual-grade-is-grade-not-orientation = dual-grade₃-involution
