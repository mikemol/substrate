------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuisfinite
--
-- Defines: coemit-mu-is-finite
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuisfinite where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Len
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectiveisfinite
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitMuCoalgebra
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuobject
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- the μ-object's projections ARE finite (bounded by depth) — the least-fixed-point/finite-trace witness.
coemit-mu-is-finite : (r : RealTrace) (n : ℕ) → len (CoemitMuCoalgebra.project coemit-mu-object μν-axis r n) ≡ n
coemit-mu-is-finite = perspective-is-finite-μν
