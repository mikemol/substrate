------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitpairingcanonical
--
-- Defines: coemit-pairing-canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitpairingcanonical where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Cocycles.V4Signature.Pairing.Type
open import Substrate.Algebra.F2.F2

open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4pairings
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4ontopairings
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- coemit-orientation-rederive +F coemit-pairing-canonical +F coemit-orbitkey-bridge.
-- CATALOG (per item): OrbitKey = Pairing × Chirality (3×2 = 6 = |S₃|) — the Stab(D)-representatives ARE (V₄-partition,
-- chirality) pairs; S4Iso/Anchor: orbit-key-to-stab-d : OrbitKey → Permutation. Pairing/Structural documents the
-- CANONICAL correspondence by COORDINATES: α-pair ↔ v4nz-α (𝟙,𝟘) ; β-pair ↔ v4nz-β (𝟘,𝟙) ; γ-pair ↔ v4nz-γ (𝟙,𝟙).
------------------------------------------------------------------------
-- (2) coemit-pairing-canonical: VERIFIED — my 344 assignment (rowSwap=(𝟙,𝟘)↦α, recip=(𝟘,𝟙)↦β, klein=(𝟙,𝟙)↦γ) matches
--     the canonical Pairing↔V4-Nonzero coordinates EXACTLY. The V4Full generators carry the canonical coords.
coemit-pairing-canonical : (coemit-v4-pairings 𝟙 𝟘 ≡ α-pair)      -- rowSwap coords (𝟙,𝟘) — canonical α
                         × ((coemit-v4-pairings 𝟘 𝟙 ≡ β-pair)      -- recip   coords (𝟘,𝟙) — canonical β
                         × (coemit-v4-pairings 𝟙 𝟙 ≡ γ-pair))      -- klein   coords (𝟙,𝟙) — canonical γ
coemit-pairing-canonical = coemit-v4-onto-pairings
