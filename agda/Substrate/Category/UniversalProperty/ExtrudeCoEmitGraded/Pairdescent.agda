------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairdescent
--
-- Defines: pair-descent
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairdescent where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Iterate
  renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.Chain
  renaming (chain to Rchain)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrefinementpair
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Ppair
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairprefixed
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


pair-descent : (n : ℕ) → Riterate coemit-refinement-pair (suc n) P⁰-pair R⊑ᶠ Riterate coemit-refinement-pair n P⁰-pair
pair-descent = Rchain coemit-refinement-pair pair-pre-fixed
