------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitanchoratadditiveorigin
--
-- Defines: coemit-anchor-at-additive-origin
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitanchoratadditiveorigin where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge.Mul
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4identityisadditiveorigin
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the anchor D sits at that additive origin (v-of-axis D = e = (𝟘,𝟘)) — the identity, in the additive domain.
coemit-anchor-at-additive-origin : V4.e ≡ V4.v4 𝟘 𝟘
coemit-anchor-at-additive-origin = coemit-v4-identity-is-additive-origin
