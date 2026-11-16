------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Duality.OrthogonalLC2
--
-- Defines: orthogonal-L₆-c
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Duality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Duality.OrthogonalLC2 where

open import Substrate.Algebra.F2.FanoPlane
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Vector.DotProduct
open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.Foundation.Eq
open import Substrate.ShadowArchitecture.Duality.NormalVector
open import Substrate.ShadowArchitecture.Duality.Bot


orthogonal-L₆-c : normal-vector L₆ ⊥ p₁₁₁
orthogonal-L₆-c = refl
