------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4genscommute
--
-- Defines: coemit-v4-gens-commute
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4genscommute where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4


coemit-v4-gens-commute : V4._·_ V4.rowSwap-gen V4.recip-gen ≡ V4._·_ V4.recip-gen V4.rowSwap-gen
coemit-v4-gens-commute = V4.gens-commute
