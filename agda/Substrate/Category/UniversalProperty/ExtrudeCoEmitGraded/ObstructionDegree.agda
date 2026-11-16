------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.ObstructionDegree
--
-- Defines: ObstructionDegree
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.ObstructionDegree where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Empty.Bot
  renaming (⊥ to Bot)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeupto
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- obstruction-degree: the ℕ-valued degree of the graded obstruction (the nilpotency degree, dⁿ=0). Between r,t
-- the degree n means: they AGREE up to grade n but DISAGREE at (suc n) — the FIRST-disagreement grade. Unique
-- (obstruction-persists: once disagreeing, forever), and n is the "cost" the residue count q (cover-the-cycle)
-- and the CrossMix nilpotency degree both name. Coherence (bisimilar) = NO finite degree (agrees at all grades).
------------------------------------------------------------------------

-- the obstruction degree: agree up to n, disagree at (suc n) — the first-disagreement grade (the residue count q).
ObstructionDegree : RealTrace → RealTrace → ℕ → Set
ObstructionDegree r t n = agree-upto n r t × (agree-upto (suc n) r t → Bot)
