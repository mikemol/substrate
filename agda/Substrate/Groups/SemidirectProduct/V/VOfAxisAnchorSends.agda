------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.V.VOfAxisAnchorSends
--
-- Defines: v-of-axis-anchor-sends
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.SemidirectProduct.V; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.V.VOfAxisAnchorSends where

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
open import Substrate.Groups.SemidirectProduct.V.VOfAxisAnchor
open import Substrate.Groups.SemidirectProduct.V.VSendsD
open import Substrate.Groups.SemidirectProduct.V.NonDSends
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Groups.V4.Operations as V4



v-of-axis-anchor-sends :
  (X x : Axis) → act-axis (v-of-axis-anchor X x) X ≡ x
v-of-axis-anchor-sends D x = v-sends-D x
v-of-axis-anchor-sends C x = non-D-sends C x
v-of-axis-anchor-sends S x = non-D-sends S x
v-of-axis-anchor-sends W x = non-D-sends W x
