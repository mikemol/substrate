------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pair
--
-- Defines: νΦ-pair
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pair where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.Iterate
  renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RTPair
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrefinementpair
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Ppair
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- THE FORMAL GFP: the intersection of the descending chain (present at all grades).
νΦ-pair : RTPair → Set
νΦ-pair (r , t) = (n : ℕ) → Riterate coemit-refinement-pair n P⁰-pair (r , t)
