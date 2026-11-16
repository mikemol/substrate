------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisv4note
--
-- Defines: axis→v4-not-e
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisv4note where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.Bot
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisv4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- no axis maps to the identity: the 3 axes are exactly V₄'s NON-identity part (the involutions), as 342 verified.
axis→v4-not-e : (a : GradingAxis) → axis→v4 a ≡ V₄.e → ⊥
axis→v4-not-e μν-axis        ()
axis→v4-not-e head-tail-axis ()
axis→v4-not-e cyc-aper-axis  ()
