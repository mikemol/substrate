------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.CongruenceAct
--
-- congruence-act T M = (i, j) ↦ bilinear-form-of M (T eᵢ) (T eⱼ).
-- The generic T^T M T action. Preservation of symmetry is a derived
-- consequence (deferred slice).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.CongruenceAct where

open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.SymBilinForm.BilinForm using (BilinForm)
open import Substrate.Algebra.F2.SymBilinForm.BilinearFormOf using (bilinear-form-of)

congruence-act : ∀ {n} → Linear n n → BilinForm n → BilinForm n
congruence-act T M i j =
  bilinear-form-of M (apply T (basis i)) (apply T (basis j))
