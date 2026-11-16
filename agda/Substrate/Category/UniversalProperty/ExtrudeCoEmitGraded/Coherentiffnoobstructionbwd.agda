------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coherentiffnoobstructionbwd
--
-- Defines: coherent-iff-no-obstruction-bwd
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coherentiffnoobstructionbwd where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeupto
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreelimit
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


coherent-iff-no-obstruction-bwd : (r t : RealTrace) → ((n : ℕ) → agree-upto n r t) → t ~ r
coherent-iff-no-obstruction-bwd r t agr = agree-limit r t agr
