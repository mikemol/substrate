------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.V.VForAnchor
--
-- Defines: v-for-anchor
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.SemidirectProduct.V; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.V.VForAnchor where

open import Substrate.Axes.Axis
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Axes.VOfAxis
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.SemidirectProduct.V.Private
open import Substrate.Groups.SemidirectProduct.V.VOfAxisAnchor
open import Substrate.Groups.SemidirectProduct.V.VFor
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Groups.V4.Operations as V4



------------------------------------------------------------------------
-- Anchor-parametric v-for. X=D specialisation IS v-for (definitionally).
------------------------------------------------------------------------

v-for-anchor : Axis → Permutation → V₄
v-for-anchor X σ = v-of-axis-anchor X (apply σ X)
