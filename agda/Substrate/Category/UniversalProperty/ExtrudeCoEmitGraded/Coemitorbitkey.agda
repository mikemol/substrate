------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitkey
--
-- Defines: coemit-orbitkey
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitkey where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Cocycles.V4Signature.Chirality.Type
open import Substrate.Cocycles.V4Signature.Pairing.Type
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (3) coemit-orbitkey-bridge: |OrbitKey| = |Pairing × Chirality| = 3 × 2 = 6 = |S₃| = |Stab(D)|. The 6 orbit-keys are
--     NOT coemit's 3 axes — they are (V₄-partition , chirality) pairs indexing the Stab(D)-representatives.
--     coemit's 3 GradingAxis are the 3 NON-ANCHOR AXES (the OBJECTS, 343); the 6 orbit-keys are the S₃-REPS.
coemit-orbitkey : Set
coemit-orbitkey = Pairing × Chirality      -- = OrbitKey (6 elements = |S₃| = |Stab(D)|), the canonical shape
