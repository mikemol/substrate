------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitfourareobjectsinv4
--
-- Defines: coemit-four-are-objects-in-v4
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitfourareobjectsinv4 where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Axes.Axis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the 4 D,C,S,W are OBJECTS in a V₄ (four tied things) — the V₄-torsor carrier, anchored at D (v-of-axis D = e).
coemit-four-are-objects-in-v4 : Axis
coemit-four-are-objects-in-v4 = D              -- the torsor basepoint; C,S,W ↦ α,β,γ (the other three objects)
