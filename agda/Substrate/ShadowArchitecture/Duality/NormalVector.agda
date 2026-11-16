------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Duality.NormalVector
--
-- Defines: normal-vector
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Duality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Duality.NormalVector where

open import Substrate.Algebra.F2.FanoPlane
open import Substrate.Algebra.F2.F2
open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 1. Normal-vector map.
--
-- The line → point function realising the self-duality. Defined by
-- direct case analysis on the line; correctness (orthogonality with
-- every point on the line) is proven below.
------------------------------------------------------------------------

normal-vector : FanoLine → Point
normal-vector L₁ = p₀₀₁
normal-vector L₂ = p₀₁₀
normal-vector L₃ = p₁₀₀
normal-vector L₄ = p₀₁₁
normal-vector L₅ = p₁₀₁
normal-vector L₆ = p₁₁₀
normal-vector L₇ = p₁₁₁
