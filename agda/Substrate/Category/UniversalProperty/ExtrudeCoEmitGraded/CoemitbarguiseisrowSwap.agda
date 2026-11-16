------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitbarguiseisrowSwap
--
-- Defines: coemit-bar-guise-is-rowSwap
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitbarguiseisrowSwap where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Digittov4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4


-- the GUISE, literal: bar's generator is rowSwap (det-flip/chirality); bar₂'s is recip (the object side).
coemit-bar-guise-is-rowSwap : digit-to-v4 (pflip 0) ≡ V4.rowSwap-gen     -- pflip 0 = 1 ⇒ (𝟙,𝟘) = rowSwap-gen
coemit-bar-guise-is-rowSwap = refl
