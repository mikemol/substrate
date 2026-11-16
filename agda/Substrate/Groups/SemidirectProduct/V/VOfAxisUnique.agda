------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.V.VOfAxisUnique
--
-- Defines: v-of-axis-unique
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.SemidirectProduct.V; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.V.VOfAxisUnique where

open import Substrate.Axes.Axis
open import Substrate.Axes.ActAxis
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Axes.VOfAxis
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Groups.V4.Operations as V4



------------------------------------------------------------------------
-- Uniqueness of v-of-axis (the only V₄ element sending D to x).
------------------------------------------------------------------------

v-of-axis-unique :
  (v : V₄) (x : Axis) → act-axis v D ≡ x → v ≡ v-of-axis x
v-of-axis-unique e D refl = refl
v-of-axis-unique α C refl = refl
v-of-axis-unique β S refl = refl
v-of-axis-unique γ W refl = refl
