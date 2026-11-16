------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemulcollapses
--
-- Defines: trace-mul-collapses
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemulcollapses where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the threading collapses to z (the zero-trace) — trace-mul r s ~ zero-trace (square-zero: every product is 0).
trace-mul-collapses : (r s : RealTrace) → trace-mul r s ~ᵗ zero-trace
head~ (trace-mul-collapses r s) = refl
tail~ (trace-mul-collapses r s) = trace-mul-collapses (RealTrace.tail r) (RealTrace.tail s)
