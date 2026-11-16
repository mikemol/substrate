------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstabcomponentfixesanchor
--
-- Defines: coemit-stab-component-fixes-anchor
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstabcomponentfixesanchor where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Axes.Axis

open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.SemidirectProduct.S
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the s-component FIXES the anchor (the ⋊'s Stab(D) side). NB Stab D τ = applyₛ τ D ≡ D DEFINITIONALLY (346),
-- so this is exactly `Stab D (s-for-anchor D σ)` — the canonical statement that the S₃-part stabilizes the anchor.
coemit-stab-component-fixes-anchor : (σ : Permutation) → Stab D (s-for-anchor D σ)
coemit-stab-component-fixes-anchor = s-for-fixes-anchor D
