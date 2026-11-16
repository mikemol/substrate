------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.V.VFor
--
-- Defines: v-for
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.SemidirectProduct.V; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.V.VFor where

open import Substrate.Axes.Axis
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Axes.VOfAxis
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.SemidirectProduct.V.Private
open import Substrate.Groups.SemidirectProduct.V.VOfAxisAnchor
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Groups.V4.Operations as V4



------------------------------------------------------------------------
-- v-for σ: the V₄ element σ agrees with on D.
-- Defined as the anchor-parametric form at D; the definitional
-- special-case in v-of-axis-anchor makes v-for σ ≡ v-of-axis (σ D).
------------------------------------------------------------------------

v-for : Permutation → V₄
v-for σ = v-of-axis-anchor D (apply σ D)
