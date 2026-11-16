------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4component
--
-- Defines: coemit-v4-component
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4component where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Axes.Axis

open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.SemidirectProduct.V.Private
open import Substrate.Groups.SemidirectProduct.V.VFor
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (2) coemit-v4-component: the V₄-component of the ⋊ factorization σ = v · s (v = v-for σ ∈ V₄; s = s-for σ ∈ Stab(D)).

-- the V₄-component: v-for σ = v-of-axis-anchor D (applyₛ σ D) — literally "WHERE σ SENDS THE ANCHOR D".
coemit-v4-component : Permutation → V₄
coemit-v4-component = v-for
