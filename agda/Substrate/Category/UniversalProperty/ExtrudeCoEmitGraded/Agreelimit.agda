------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreelimit
--
-- Defines: agree-limit
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreelimit where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Prefixseparates
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeupto
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


-- the LIMIT is SUBSTANTIVE: agreeing at EVERY grade ⇒ bisimilar to r (the gfp = the ~-class of r).
agree-limit : (r t : RealTrace) → ((n : ℕ) → agree-upto n r t) → t ~ r
agree-limit r t agr = prefix-separates t r agr
