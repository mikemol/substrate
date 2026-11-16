------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipscommute
--
-- Defines: v4-flips-commute
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipscommute where

open import Substrate.Category.Allegory.Refinement.Preamble
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipmorph
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipobj
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- and they COMMUTE (disjoint components): flipping morph then obj = flipping obj then morph.
v4-flips-commute : (v : V4.V4Full) → v4-flip-obj (v4-flip-morph v) ≡ v4-flip-morph (v4-flip-obj v)
v4-flips-commute (V4.v4 a b) = refl
