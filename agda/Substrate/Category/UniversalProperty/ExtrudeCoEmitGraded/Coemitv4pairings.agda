------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4pairings
--
-- Defines: coemit-v4-pairings
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4pairings where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Cocycles.V4Signature.Pairing.Type
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (2) coemit-v4-acts-on-four: V₄'s three non-identity elements are the three PARTITIONS of the 4 axes (Pairing:
--     α-pair, β-pair, γ-pair) — NOT the axes themselves (343's correction). Reuse the canonical Pairing type.

-- V₄'s 3 non-identity elements ↔ the 3 axis-PARTITIONS (each double-transposition pairs the 4 axes into 2+2).
-- GENUINE map on the (morph,obj) F₂-components: rowSwap=(𝟙,𝟘)↦α, recip=(𝟘,𝟙)↦β, klein=(𝟙,𝟙)↦γ (identity ↦ α, degenerate).
coemit-v4-pairings : F₂ → F₂ → Pairing
coemit-v4-pairings 𝟙 𝟘 = α-pair      -- rowSwap-gen: the det-flip pairing
coemit-v4-pairings 𝟘 𝟙 = β-pair      -- recip-gen: the object-side pairing
coemit-v4-pairings 𝟙 𝟙 = γ-pair      -- klein: the central 180° pairing
coemit-v4-pairings 𝟘 𝟘 = α-pair      -- identity: no proper pairing (degenerate; the 3 NON-identity elements pair)
