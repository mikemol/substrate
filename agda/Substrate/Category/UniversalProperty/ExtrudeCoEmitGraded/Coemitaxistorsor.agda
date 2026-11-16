------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitaxistorsor
--
-- Defines: coemit-axis-torsor
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitaxistorsor where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Axes.Axis
open import Substrate.Axes.Axis.Compose
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisfixunit
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- Axis AS Lawvere's TorsorAtom, anchored at D — 347's sentence, now a record.
coemit-axis-torsor : TorsorAtom Axis
coemit-axis-torsor = record { _∙_ = _∙ᴬ_ ; e = D ; fix→unit = axis-fix→unit }
