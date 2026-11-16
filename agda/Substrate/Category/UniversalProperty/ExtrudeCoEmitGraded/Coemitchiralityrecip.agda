------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitchiralityrecip
--
-- Defines: coemit-chirality-recip
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitchiralityrecip where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Cocycles.V4Signature.Chirality.Type
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4


coemit-chirality-recip : V4.chirality-of V4.recip-gen ≡ even       -- recip is EVEN (in A₄) — the object-side generator
coemit-chirality-recip = V4.chirality-recip-even
