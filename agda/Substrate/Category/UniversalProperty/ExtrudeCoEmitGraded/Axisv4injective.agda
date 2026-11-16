------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisv4injective
--
-- Defines: axis→v4-injective
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisv4injective where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisv4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- the embedding is INJECTIVE (the 3 axes are 3 DISTINCT non-identity V₄ elements — no axis is the identity e).
axis→v4-injective : (a b : GradingAxis) → axis→v4 a ≡ axis→v4 b → a ≡ b
axis→v4-injective μν-axis        μν-axis        _ = refl
axis→v4-injective head-tail-axis head-tail-axis _ = refl
axis→v4-injective cyc-aper-axis  cyc-aper-axis  _ = refl
