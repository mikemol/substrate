------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Takevec
--
-- Defines: take-vec
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Takevec where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- coemit-graded-take-coherence: link the graded carrier C n = Vec ℕ n to the ACTUAL trace. take-vec builds the
-- grade-n prefix by recon (grade-raising with the head digit); it forgets to the flat take (the shadow). So the
-- graded prefix and the flat observation agree — the instance is anchored to coemit-trace, not free-floating.
------------------------------------------------------------------------

-- the graded prefix of a trace (C n = Vec ℕ n), built forward by the coalgebra head/tail.
take-vec : (n : ℕ) → RealTrace → Vec ℕ n
take-vec zero    _ = []
take-vec (suc n) r = RealTrace.head r ∷ take-vec n (RealTrace.tail r)
