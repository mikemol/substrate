------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4kleincentral
--
-- Defines: coemit-v4-klein-central
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4kleincentral where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4


coemit-v4-klein-central : V4._·_ V4.klein V4.klein ≡ V4.e            -- the 180° central element is an involution
coemit-v4-klein-central = V4.klein-invol
