------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Duality.DualLineNormal
--
-- Defines: dual-line-normal
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Duality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Duality.DualLineNormal where

open import Substrate.Algebra.F2.FanoPlane
open import Substrate.Foundation.Product
open import Substrate.Algebra.F2.F2
open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.Foundation.Eq
open import Substrate.ShadowArchitecture.Duality.NormalVector
open import Substrate.ShadowArchitecture.Duality.DualLine
open import Substrate.ShadowArchitecture.Duality.LineCover



dual-line-normal : ∀ (ℓ : FanoLine) → dual-line (normal-vector ℓ) ≡ ℓ
dual-line-normal =
  line-cover _ (refl , refl , refl , refl , refl , refl , refl)
