------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.SquareZeroUpTo
--
-- Defines: SquareZeroUpTo
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.SquareZeroUpTo where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (1) the SHARED square-zero law: a binary op that collapses its diagonal to z (the ∂²=0 / d²=0 shape). trace-mul
-- satisfies it (the μ/simplicial-boundary side). This is the SHAPE SimplicialBoundary's ∂∘∂≡0 has — shared LAW,
-- not shared carrier (RealTrace vs ordered face-lists; the literal ≡ is verified-FALSE, the law is shared).
SquareZeroUpTo : (RealTrace → RealTrace → RealTrace) → RealTrace → Set
SquareZeroUpTo op z = (x : RealTrace) → op x x ~ z
