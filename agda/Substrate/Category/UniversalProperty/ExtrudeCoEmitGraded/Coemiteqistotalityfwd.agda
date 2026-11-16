------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemiteqistotalityfwd
--
-- Defines: coemit-eq-is-totality-fwd
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemiteqistotalityfwd where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Prefixseparates
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bisimprefix
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitagreesisbisimfwd
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


-- THE TOTALITY: on the coinductive carrier, ≡ is the conjunction over ALL finite perspectives (the orbit's actions).
-- This is not "settling for ~": it is ≡, CONSTRUCTED. (Reusing 331/335: prefix-separates + bisim→prefix.)
coemit-eq-is-totality-fwd : (r t : RealTrace) → ((n : ℕ) → take n t ≡ take n r) → t ~ r
coemit-eq-is-totality-fwd = coemit-agrees-is-bisim-fwd
