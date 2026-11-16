------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdigit4periodic
--
-- Defines: coemit-digit-4-periodic
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdigit4periodic where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Digittov4
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Parity4periodic
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bit14periodic
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Trans
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4


coemit-digit-4-periodic : (n : ℕ) → digit-to-v4 (suc (suc (suc (suc n)))) ≡ digit-to-v4 n
coemit-digit-4-periodic n = cong₂ V4.v4 (parity-4-periodic n) (bit1-4-periodic n)
