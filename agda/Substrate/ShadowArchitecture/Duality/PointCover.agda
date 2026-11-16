------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Duality.PointCover
--
-- Defines: point-cover
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Duality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Duality.PointCover where

open import Substrate.Algebra.F2.FanoPlane
open import Substrate.Foundation.Product
open import Substrate.Algebra.F2.F2
open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 3. Round-trip: the two maps are mutually inverse.
--
-- Per [[feedback-expose-generator-not-orbit-applies]] Layer 1 — the
-- 7-constructor Point/FanoLine enumerations collapse via per-type covers
-- that dispatch a heterogeneous refl-tuple. Each refl literal infers
-- its own implicit {x}.
------------------------------------------------------------------------

point-cover :
  ∀ {ℓ} (P : Point → Set ℓ) →
  P p₀₀₁ × P p₀₁₀ × P p₁₀₀ × P p₀₁₁ × P p₁₀₁ × P p₁₁₀ × P p₁₁₁ →
  ∀ p → P p
point-cover _ (p , _ , _ , _ , _ , _ , _) p₀₀₁ = p
point-cover _ (_ , p , _ , _ , _ , _ , _) p₀₁₀ = p
point-cover _ (_ , _ , p , _ , _ , _ , _) p₁₀₀ = p
point-cover _ (_ , _ , _ , p , _ , _ , _) p₀₁₁ = p
point-cover _ (_ , _ , _ , _ , p , _ , _) p₁₀₁ = p
point-cover _ (_ , _ , _ , _ , _ , p , _) p₁₁₀ = p
point-cover _ (_ , _ , _ , _ , _ , _ , p) p₁₁₁ = p
