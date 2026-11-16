------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairbisim
--
-- Defines: νΦ-pair→bisim
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairbisim where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreelimit
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairiteragree
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pair
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- THE BRIDGE (both directions): the refinement's gfp IS the carrier's bisimilarity (the two Φ's limits coincide).
νΦ-pair→bisim : (r t : RealTrace) → νΦ-pair (r , t) → t ~ r
νΦ-pair→bisim r t f = agree-limit r t (λ n → pair-iter→agree n r t (f n))
