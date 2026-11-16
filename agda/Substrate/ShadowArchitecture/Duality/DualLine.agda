------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Duality.DualLine
--
-- Defines: dual-line
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Duality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Duality.DualLine where

open import Substrate.Algebra.F2.FanoPlane
open import Substrate.Algebra.F2.F2
open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.Foundation.Eq
open import Substrate.ShadowArchitecture.Duality.NormalVector



------------------------------------------------------------------------
-- 2. Inverse: dual-line map.
--
-- The inverse Point → FanoLine of normal-vector. Defined directly; that
-- normal-vector ∘ dual-line ≡ id and dual-line ∘ normal-vector ≡ id
-- are stated as round-trip lemmas below (each closes by case analysis
-- +F refl).
------------------------------------------------------------------------

dual-line : Point → FanoLine
dual-line p₀₀₁ = L₁
dual-line p₀₁₀ = L₂
dual-line p₁₀₀ = L₃
dual-line p₀₁₁ = L₄
dual-line p₁₀₁ = L₅
dual-line p₁₁₀ = L₆
dual-line p₁₁₁ = L₇
