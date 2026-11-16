------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorientationischirality
--
-- Defines: coemit-orientation-is-chirality
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorientationischirality where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Cocycles.V4Signature.Chirality.Type
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4


-- (3) coemit-retract-dual-grade (HONESTY / RETRACTION): 334 set orientation-flip = dual-grade₃ (Hodge's Λᵏ↔Λⁿ⁻ᵏ
--     GRADE involution). The CANONICAL orientation is CHIRALITY = which coset of A₄ in S₄ (even/odd, Chirality).
--     These are DIFFERENT involutions: dual-grade₃ reflects GRADES (Λ⁰↔Λ³, Λ¹↔Λ²); chirality flips the A₄-COSET.
--     RETRACTED: dual-grade₃ is a genuine involution but is NOT the orientation. Both stand, under correct names.
coemit-orientation-is-chirality : V4.chirality-of V4.rowSwap-gen ≡ odd    -- THE orientation: S₄/A₄ parity (canonical)
coemit-orientation-is-chirality = V4.chirality-rowSwap
