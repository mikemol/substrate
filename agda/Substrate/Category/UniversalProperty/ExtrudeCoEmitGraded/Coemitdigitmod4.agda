------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdigitmod4
--
-- Defines: coemit-digit-mod4
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdigitmod4 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Digittov4
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdigit4periodic
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Mod4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Trans


-- THE FIBRE, literal: digit-to-v4 factors through ℕ/4 (the map is constant on residue classes).
coemit-digit-mod4 : (n : ℕ) → digit-to-v4 n ≡ digit-to-v4 (mod4 n)
coemit-digit-mod4 zero                        = refl
coemit-digit-mod4 (suc zero)                  = refl
coemit-digit-mod4 (suc (suc zero))            = refl
coemit-digit-mod4 (suc (suc (suc zero)))      = refl
coemit-digit-mod4 (suc (suc (suc (suc n))))   =
  trans (coemit-digit-4-periodic n) (coemit-digit-mod4 n)
