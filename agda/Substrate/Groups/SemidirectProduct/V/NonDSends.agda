------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.V.NonDSends
--
-- Defines: non-D-sends
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.SemidirectProduct.V; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.V.NonDSends where

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
open import Substrate.Groups.SemidirectProduct.V.VSendsD
open import Substrate.Groups.SemidirectProduct.V.SelfToD
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Groups.V4.Operations as V4


non-D-sends :
  (Y x : Axis) → act-axis (v-of-axis x V4.· v-of-axis Y) Y ≡ x
non-D-sends Y x =
  trans (act-axis-∙ (v-of-axis x) (v-of-axis Y) Y)
        (trans (cong (act-axis (v-of-axis x)) (self-to-D Y))
               (v-sends-D x))
