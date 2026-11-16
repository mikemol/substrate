------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Takecoherence
--
-- Defines: take-coherence
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Takecoherence where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Forgetgrade
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Takevec
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


-- (b) the graded prefix forgets to the flat take (the shadow) — by induction on the grade.
take-coherence : (n : ℕ) (r : RealTrace) → forget-grade (take-vec n r) ≡ take n r
take-coherence zero    r = refl
take-coherence (suc n) r = cong (RealTrace.head r ∷_) (take-coherence n (RealTrace.tail r))
