------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorientationof
--
-- Defines: coemit-orientation-of
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorientationof where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Cocycles.V4Signature.Chirality.Type
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4


-- (1) coemit-orientation-rederive (DISCHARGING 344's RETRACTION): the orientation component of an orbit-key is the
--     CHIRALITY (S₄/A₄ parity), NOT dual-grade₃. Re-derived: the orientation of a V₄ element is chirality-of it.
coemit-orientation-of : V4.V4Full → Chirality
coemit-orientation-of = V4.chirality-of          -- THE orientation (canonical): which coset of A₄ in S₄
