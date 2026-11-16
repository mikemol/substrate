------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Duality.LineCover
--
-- Defines: line-cover
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Duality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Duality.LineCover where

open import Substrate.Algebra.F2.FanoPlane
open import Substrate.Foundation.Product
open import Substrate.Algebra.F2.F2
open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.Foundation.Eq


line-cover :
  ∀ {ℓ} (P : FanoLine → Set ℓ) →
  P L₁ × P L₂ × P L₃ × P L₄ × P L₅ × P L₆ × P L₇ →
  ∀ l → P l
line-cover _ (p , _ , _ , _ , _ , _ , _) L₁ = p
line-cover _ (_ , p , _ , _ , _ , _ , _) L₂ = p
line-cover _ (_ , _ , p , _ , _ , _ , _) L₃ = p
line-cover _ (_ , _ , _ , p , _ , _ , _) L₄ = p
line-cover _ (_ , _ , _ , _ , p , _ , _) L₅ = p
line-cover _ (_ , _ , _ , _ , _ , p , _) L₆ = p
line-cover _ (_ , _ , _ , _ , _ , _ , p) L₇ = p
