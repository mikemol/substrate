------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Duality.NormalDualLine
--
-- Defines: normal-dual-line
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Duality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Duality.NormalDualLine where

open import Substrate.Algebra.F2.FanoPlane
open import Substrate.Foundation.Product
open import Substrate.Algebra.F2.F2
open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.Foundation.Eq
open import Substrate.ShadowArchitecture.Duality.NormalVector
open import Substrate.ShadowArchitecture.Duality.DualLine
open import Substrate.ShadowArchitecture.Duality.PointCover



normal-dual-line : ∀ (p : Point) → normal-vector (dual-line p) ≡ p
normal-dual-line =
  point-cover _ (refl , refl , refl , refl , refl , refl , refl)
