------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbarguiseisrecip
--
-- Defines: coemit-bar₂-guise-is-recip
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbarguiseisrecip where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Digittov4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4


coemit-bar₂-guise-is-recip : digit-to-v4 (xor2 0) ≡ V4.recip-gen         -- xor2 0 = 2 ⇒ (𝟘,𝟙) = recip-gen
coemit-bar₂-guise-is-recip = refl
