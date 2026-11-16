------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bit14periodic
--
-- Defines: bit1-4-periodic
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bit14periodic where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bit1
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Digittov4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- (3) coemit-digit-quotient: digit-to-v4 : ℕ ↠ V4Full is 4-PERIODIC — its fibre is exactly n mod 4 — and it hits
--     all four V₄ elements (0 ↦ e, 1 ↦ rowSwap, 2 ↦ recip, 3 ↦ klein). So ℕ/4 ≅ V₄ under digit-to-v4.
------------------------------------------------------------------------
bit1-4-periodic : (n : ℕ) → bit1 (suc (suc (suc (suc n)))) ≡ bit1 n
bit1-4-periodic n = refl
