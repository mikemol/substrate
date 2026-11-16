------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4roundtrip
--
-- Defines: coemit-s4-roundtrip
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4roundtrip where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Cocycles.V4Signature.S4Iso.Anchor
open import Substrate.Cocycles.V4Signature.S4Iso.Roundtrips
open import Substrate.Cocycles.V4Signature.S4Iso.Classify
open import Substrate.Axes.Axis

open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Eq Axis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (3) coemit-s4-roundtrip: the canonical Stab(D) roundtrip — every D-stabilizing permutation is recovered (up to ≈)
--     from its orbit-key. Reuse Roundtrips.stab-round-trip. This is the ⋊'s uniqueness: σ = v·s with s ∈ Stab(D).
coemit-s4-roundtrip : (σ : Permutation) (σ-stab : Stab D σ)
                    → orbit-key-to-stab-d (stab-d-to-orbit-key σ σ-stab) ≈ σ
coemit-s4-roundtrip = stab-round-trip
