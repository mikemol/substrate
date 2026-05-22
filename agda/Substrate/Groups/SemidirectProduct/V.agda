------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.V
--
-- The V₄-side of the semidirect product:
--   * v-of-axis-sends-D    : v-of-axis x sends D to x      (4 refls on Axis)
--   * v-of-axis-unique     : v-of-axis is the unique V₄ element with the property
--   * v-for σ              : the V₄ element σ agrees with on D
--   * v-of-axis-anchor     : anchor-parametric generator
--   * v-of-axis-anchor-sends, v-for-anchor, v-for-anchor-sends
--
-- The 4-axis specialisations (v-of-axis-sends-{C,S,W}, etc.) are gone:
-- the anchor-parametric form IS the generator; the per-axis siblings
-- were orbit-cataloguing pre-generator (a partial-coset-detector
-- artifact, now redundant).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.V where

open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W; act-axis)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.S4
  using (Permutation)
  renaming (apply to applyₛ)
open import Substrate.Groups.V4-Embedding
  using (v-of-axis; axis-of-v; act-axis-∙; act-axis-as-V₄-mult)

------------------------------------------------------------------------
-- Uniqueness of v-of-axis (the only V₄ element sending D to x).
------------------------------------------------------------------------

v-of-axis-unique :
  (v : V₄) (x : Axis) → act-axis v D ≡ x → v ≡ v-of-axis x
v-of-axis-unique e D refl = refl
v-of-axis-unique α C refl = refl
v-of-axis-unique β S refl = refl
v-of-axis-unique γ W refl = refl

------------------------------------------------------------------------
-- Anchor-parametric generator.
--
-- The D-anchored case is special-cased to `v-of-axis x` directly, so
-- `v-of-axis-anchor D x ≡ v-of-axis x` holds DEFINITIONALLY (not just
-- propositionally via ε-right). This is the structural fact that lets
-- the D-specialized callsites (the cocycle's anchor) use the
-- parametric form without cast.
------------------------------------------------------------------------

v-of-axis-anchor : Axis → Axis → V₄
v-of-axis-anchor D x = v-of-axis x
v-of-axis-anchor X x = v-of-axis x V4.· v-of-axis X

private
  -- Internal helper: D-anchored sends-property by 4-refl enumeration.
  -- Was previously the public `v-of-axis-sends-D`; now hidden — callers
  -- use `v-of-axis-anchor-sends D` (which dispatches here in the D-case
  -- with no cast, because v-of-axis-anchor D x ≡ v-of-axis x definitionally).
  v-sends-D : (x : Axis) → act-axis (v-of-axis x) D ≡ x
  v-sends-D D = refl
  v-sends-D C = refl
  v-sends-D S = refl
  v-sends-D W = refl

  -- Internal helper: act-axis (v-of-axis Y) Y ≡ D, via act-axis-as-V₄-mult
  -- and V₄ self-inverse.
  self-to-D : (Y : Axis) → act-axis (v-of-axis Y) Y ≡ D
  self-to-D Y =
    trans (act-axis-as-V₄-mult (v-of-axis Y) Y)
          (cong axis-of-v (V4.inv-left (v-of-axis Y)))

  -- Internal helper: the non-D anchor-sends body. Generic over the
  -- anchor Y (called only at Y ∈ {C, S, W}).
  non-D-sends :
    (Y x : Axis) → act-axis (v-of-axis x V4.· v-of-axis Y) Y ≡ x
  non-D-sends Y x =
    trans (act-axis-∙ (v-of-axis x) (v-of-axis Y) Y)
          (trans (cong (act-axis (v-of-axis x)) (self-to-D Y))
                 (v-sends-D x))

v-of-axis-anchor-sends :
  (X x : Axis) → act-axis (v-of-axis-anchor X x) X ≡ x
v-of-axis-anchor-sends D x = v-sends-D x
v-of-axis-anchor-sends C x = non-D-sends C x
v-of-axis-anchor-sends S x = non-D-sends S x
v-of-axis-anchor-sends W x = non-D-sends W x

------------------------------------------------------------------------
-- v-for σ: the V₄ element σ agrees with on D.
-- Defined as the anchor-parametric form at D; the definitional
-- special-case in v-of-axis-anchor makes v-for σ ≡ v-of-axis (σ D).
------------------------------------------------------------------------

v-for : Permutation → V₄
v-for σ = v-of-axis-anchor D (applyₛ σ D)

------------------------------------------------------------------------
-- Anchor-parametric v-for. X=D specialisation IS v-for (definitionally).
------------------------------------------------------------------------

v-for-anchor : Axis → Permutation → V₄
v-for-anchor X σ = v-of-axis-anchor X (applyₛ σ X)

v-for-anchor-sends :
  (X : Axis) (σ : Permutation) → act-axis (v-for-anchor X σ) X ≡ applyₛ σ X
v-for-anchor-sends X σ = v-of-axis-anchor-sends X (applyₛ σ X)
