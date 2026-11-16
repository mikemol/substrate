------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.V.VForAnchorSends
--
-- Defines: v-for-anchor-sends
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.SemidirectProduct.V; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.V.VForAnchorSends where

open import Substrate.Axes.Axis
open import Substrate.Axes.ActAxis
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Axioms.InvLeft
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Axes.VOfAxis
open import Substrate.Axes.AxisOfV
open import Substrate.Groups.V4-Embedding
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.SemidirectProduct.V.Private
open import Substrate.Groups.SemidirectProduct.V.VOfAxisAnchorSends
open import Substrate.Groups.SemidirectProduct.V.VForAnchor
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Groups.V4.Operations as V4



v-for-anchor-sends :
  (X : Axis) (σ : Permutation) → act-axis (v-for-anchor X σ) X ≡ apply σ X
v-for-anchor-sends X σ = v-of-axis-anchor-sends X (apply σ X)
