------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisfin
--
-- Defines: axis→fin
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisfin where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- (2) coemit-s3-permutation: S₃ acts on the 3 grading axes (GradingAxis). A permutation of Fin 3 (S₃) applied to
--     the 3-element axis index — the ⋊ gluing (S₄=V₄⋊S₃). Concretely: an axis ↔ Fin 3, S₃ permutes.
------------------------------------------------------------------------

axis→fin : GradingAxis → Fin 3
axis→fin μν-axis        = zero
axis→fin head-tail-axis = suc zero
axis→fin cyc-aper-axis  = suc (suc zero)
