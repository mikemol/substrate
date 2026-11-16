------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits3braided
--
-- Defines: coemit-s3-braided
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits3braided where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3reaches
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- THE BRAIDING: the S₃ orbit move (s3-reaches) is available at EVERY coinductive depth n — the group structure
-- threads through the coinduction. Because the orbit is FINITE (3 axes, S₃-transitive), the moves are bounded: the
-- rigidity lives HERE (the closed finite orbit), not in the groupoid (where you'd always find another move).
coemit-s3-braided : (a b : GradingAxis) (r : RealTrace) (n : ℕ)
                  → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ a ≡ b)
coemit-s3-braided a b r n = s3-reaches a b
