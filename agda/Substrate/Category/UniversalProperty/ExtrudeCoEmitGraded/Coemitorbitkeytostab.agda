------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitkeytostab
--
-- Defines: coemit-orbitkey-to-stab
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitkeytostab where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Cocycles.V4Signature.Chirality.Type
open import Substrate.Cocycles.V4Signature.Pairing.Type
open import Substrate.Cocycles.V4Signature.S4Iso.Anchor
open import Substrate.Axes.Axis

open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitkey
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- coemit-orbitkey-to-stab +F coemit-s4-roundtrip: the canonical OrbitKey ↔ Stab(D) maps, REUSED (not re-derived).
-- S4Iso/Anchor: orbit-key-to-stab-d : OrbitKey → Permutation (= orbit-key-to-stab-anchor D); orbit-key-to-stab-d-fixes-D
-- (the anchor IS fixed — confirming D-fixed-point-is-anchor from the canonical side).
-- S4Iso/Roundtrips: stab-round-trip : orbit-key-to-stab-d (stab-d-to-orbit-key σ σ-stab) ≈ σ.
------------------------------------------------------------------------

-- (2) coemit-orbitkey-to-stab: coemit's orbit-key (Pairing × Chirality = OrbitKey) maps to its canonical
--     Stab(D)-REPRESENTATIVE permutation. Reuse orbit-key-to-stab-d (= orbit-key-to-stab-anchor D) directly.
coemit-orbitkey-to-stab : coemit-orbitkey → Permutation
coemit-orbitkey-to-stab = orbit-key-to-stab-d
