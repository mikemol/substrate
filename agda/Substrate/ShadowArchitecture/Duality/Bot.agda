------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Duality.Bot
--
-- Defines: _⊥_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Duality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Duality.Bot where

open import Substrate.Algebra.F2.FanoPlane
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Vector.DotProduct
open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.Foundation.Eq
open import Substrate.ShadowArchitecture.Duality.NormalVector
open import Substrate.Foundation.Empty.Bot



------------------------------------------------------------------------
-- 4. Orthogonality: the normal-vector is F₂-orthogonal to every point
-- on its line.
--
-- We unfold `line-points ℓ = (a, b, c)` and state three obligations:
-- normal-vector ℓ · a ≡ 𝟘, … · b ≡ 𝟘, … · c ≡ 𝟘 (under the F₂
-- inner product `_·F_`). Each closes by `refl` because the dot
-- product reduces by computation on concrete F₂³ vectors.
--
-- We package the three obligations as a single record `Orthogonal`
-- and provide one instance per line.
------------------------------------------------------------------------

_⊥_ : Point → Point → Set
p ⊥ q = (point-to-vec p ·F point-to-vec q) ≡ 𝟘
