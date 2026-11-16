------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.V.VSendsD
--
-- Defines: v-sends-D
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.SemidirectProduct.V; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.V.VSendsD where

open import Substrate.Axes.Axis
open import Substrate.Axes.ActAxis
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Axes.VOfAxis
open import Substrate.Groups.V4-Embedding
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.SemidirectProduct.V.Private
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Groups.V4.Operations as V4


v-sends-D : (x : Axis) → act-axis (v-of-axis x) D ≡ x
v-sends-D D = refl
v-sends-D C = refl
v-sends-D S = refl
v-sends-D W = refl

-- Internal helper: act-axis (v-of-axis Y) Y ≡ D, via act-axis-as-V₄-mult
-- and V₄ self-inverse.
