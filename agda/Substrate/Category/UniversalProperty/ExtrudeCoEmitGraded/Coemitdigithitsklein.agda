------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdigithitsklein
--
-- Defines: coemit-digit-hits-klein
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdigithitsklein where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Digittov4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4

coemit-digit-hits-klein   : digit-to-v4 3 ≡ V4.klein
coemit-digit-hits-klein   = refl
