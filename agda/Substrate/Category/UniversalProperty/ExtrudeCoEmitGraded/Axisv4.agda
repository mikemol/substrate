------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisv4
--
-- Defines: axis→v4
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisv4 where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- coemit-v4-group +F coemit-s4-full-group +F coemit-rung4-genuine-action: closing 342's V₄ honest-partial by REUSING
-- the canonical group tree (D-graded-is-canonical, D-look-in-the-right-tree): Substrate.Groups.V4.Bijection has
-- `data V₄ : Set where e α β γ` (the 4-element Klein-four: identity e +F the 3 involutions α β γ), and
-- Substrate.Groups.S4-Composed builds S₄-Group = Group-bundle (to-setoid V4.V₄-Group) S₃.S₃-Group — the genuine
-- V₄ ⋊ S₃ → S₄. coemit's GradingAxis is the 3 NON-IDENTITY involutions; the canonical V₄ supplies the missing e.
------------------------------------------------------------------------

-- (1) coemit-v4-group: coemit's 3 axes ARE the 3 non-identity elements of the canonical V₄ (the missing 4th is e).
--     The embedding closes 342's honest-partial: GradingAxis ↪ V₄ (onto {α,β,γ}), with e the identity coemit lacked.
axis→v4 : GradingAxis → V₄
axis→v4 μν-axis        = α
axis→v4 head-tail-axis = β
axis→v4 cyc-aper-axis  = γ
