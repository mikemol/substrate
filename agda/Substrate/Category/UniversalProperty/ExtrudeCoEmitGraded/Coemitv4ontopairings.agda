------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4ontopairings
--
-- Defines: coemit-v4-onto-pairings
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4ontopairings where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Cocycles.V4Signature.Pairing.Type
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4pairings
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the three non-identity V₄ elements give the THREE DISTINCT partitions (the map is genuinely onto the 3 pairings).
coemit-v4-onto-pairings : (coemit-v4-pairings 𝟙 𝟘 ≡ α-pair)
                        × ((coemit-v4-pairings 𝟘 𝟙 ≡ β-pair) × (coemit-v4-pairings 𝟙 𝟙 ≡ γ-pair))
coemit-v4-onto-pairings = refl , (refl , refl)
