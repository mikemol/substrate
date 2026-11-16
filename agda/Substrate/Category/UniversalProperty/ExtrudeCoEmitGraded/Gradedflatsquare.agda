------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Gradedflatsquare
--
-- Defines: graded-flat-square
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Gradedflatsquare where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitgraded
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Forgetgrade
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Reconforget
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the ALLEGORY SQUARE (graded recon ↔ flat cons): forgetting a grade-raised prefix = flat-consing the digit.
-- This IS the graded↔flat bridge (the Φ-chain commuting square) for coemit-trace, gforget-realized.
graded-flat-square : {n : ℕ} (v : Vec ℕ n) (d : ℕ)
                   → forget-grade (recon coemit-graded n v d) ≡ (d ∷ forget-grade v)
graded-flat-square = recon-forget
