------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitDisv4identity
--
-- Defines: coemit-D-is-v4-identity
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitDisv4identity where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Axes.Axis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


coemit-D-is-v4-identity : Axis                        -- D is the axis at V₄'s identity (v-of-axis D = e) — the anchor
coemit-D-is-v4-identity = D
