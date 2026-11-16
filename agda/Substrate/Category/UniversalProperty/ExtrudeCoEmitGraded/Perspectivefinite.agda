------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectivefinite
--
-- Defines: perspective-finite
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectivefinite where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the finite (μ) witness at a given depth n, per axis — each is a bounded/finite projection of the trace.
perspective-finite : GradingAxis → RealTrace → ℕ → List ℕ
perspective-finite μν-axis        r n = take n r                    -- μ: the finite prefix (bounded depth)
perspective-finite head-tail-axis r n = RealTrace.head r ∷ []                 -- head: the single finite digit (depth 1)
perspective-finite cyc-aper-axis  r n = take n r                    -- period: the finite cyclic window (bounded)
