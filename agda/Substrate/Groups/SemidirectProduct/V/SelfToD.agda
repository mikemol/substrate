------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.V.SelfToD
--
-- Defines: self-to-D
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.SemidirectProduct.V; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.V.SelfToD where

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
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Groups.V4.Operations as V4


self-to-D : (Y : Axis) → act-axis (v-of-axis Y) Y ≡ D
self-to-D Y =
  trans (act-axis-as-V₄-mult (v-of-axis Y) Y)
        (cong axis-of-v (inv-left (v-of-axis Y)))

-- Internal helper: the non-D anchor-sends body. Generic over the
-- anchor Y (called only at Y ∈ {C, S, W}).
