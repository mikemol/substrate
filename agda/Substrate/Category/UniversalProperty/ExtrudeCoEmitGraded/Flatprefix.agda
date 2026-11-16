------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Flatprefix
--
-- Defines: flat-prefix
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Flatprefix where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- THE FLAT SHADOW: the grade collapses to the flat trace-prefix (take n = gforget the whole prefix at grade n).
-- take n r : List ℕ is the flat/ungraded prefix (the shadow of the graded Vec ℕ n).
flat-prefix : ℕ → RealTrace → List ℕ
flat-prefix = take
