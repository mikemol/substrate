------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.S
--
-- The Stab(X)-side residue: s-for-anchor X σ = embed (v-for-anchor X σ) · σ.
--
-- The X=D specialisation IS s-for σ definitionally (because
-- v-of-axis-anchor D x ≡ v-of-axis x definitionally in V.agda). So
-- the D-specialised s-for-fixes-D is gone — callers use
-- `s-for-fixes-anchor D σ` which has the matching type via the
-- definitional collapse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.S where

open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)

open import Substrate.Axes.Axis using (Axis; D)
open import Substrate.Axes.ActAxis using (act-axis)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Permutation.Compose Axis using (_·_)
open import Substrate.Groups.V4-Embedding
  using (embed; act-axis-involutive)

open import Substrate.Groups.SemidirectProduct.V

------------------------------------------------------------------------
-- D-anchored residue. (X=D specialisation of s-for-anchor.)
------------------------------------------------------------------------

s-for : Permutation → Permutation
s-for σ = embed (v-for σ) · σ

------------------------------------------------------------------------
-- Anchor-parametric residue + fixing law.
------------------------------------------------------------------------

s-for-anchor : Axis → Permutation → Permutation
s-for-anchor X σ = embed (v-for-anchor X σ) · σ

s-for-fixes-anchor :
  (X : Axis) (σ : Permutation) → apply (s-for-anchor X σ) X ≡ X
s-for-fixes-anchor X σ =
  trans (cong (act-axis (v-for-anchor X σ)) (sym (v-for-anchor-sends X σ)))
        (act-axis-involutive (v-for-anchor X σ) X)
