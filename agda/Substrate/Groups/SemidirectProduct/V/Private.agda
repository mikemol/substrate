------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.V.Private
--
-- Defines: Private
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.SemidirectProduct.V; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.V.Private where

open import Substrate.Axes.Axis
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Axes.VOfAxis
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.SemidirectProduct.V.VOfAxisAnchor
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Groups.V4.Operations as V4



-- Internal helper: D-anchored sends-property by 4-refl enumeration.
-- Was previously the public `v-of-axis-sends-D`; now hidden — callers
-- use `v-of-axis-anchor-sends D` (which dispatches here in the D-case
-- with no cast, because v-of-axis-anchor D x ≡ v-of-axis x definitionally).
