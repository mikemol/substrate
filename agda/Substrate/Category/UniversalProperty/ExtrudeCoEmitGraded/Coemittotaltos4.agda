------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittotaltos4
--
-- Defines: coemit-total-to-s4
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittotaltos4 where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Cocycles.V4Signature.S4Iso.Classify
open import Substrate.Axes.Axis

open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (3) coemit-total-to-s4: the canonical TotalSpace ≃ S₄ forward map — (orbit_key , v4_delta) ↦ embed v · stab-rep.
--     This IS the ⋊ product: the V₄-element times the Stab(D)-representative. Reuse it.

coemit-total-to-s4 : TotalSpace → Permutation
coemit-total-to-s4 = total-to-s4     -- (ok , v) ↦ embed v · orbit-key-to-stab-d ok (the ⋊-product = S₄ element)
