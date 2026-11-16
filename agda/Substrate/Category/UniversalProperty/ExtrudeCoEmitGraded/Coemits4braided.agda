------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4braided
--
-- Defines: coemit-s4-braided
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4braided where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- the S₄ = V₄ ⋊ S₃ braiding (THE INVARIANT): a semidirect element is (v , σ) — a V₄ involution v PLUS an S₃
-- permutation σ; the ⋊-product twists v THROUGH σ (act φ). Modeled here as the pair (axis, perm) with the twist
-- being s3-on-axis (S₃ acting on the axis = act φ). The braiding IS this twist, threaded at every coinductive depth.
coemit-s4-braided : (a : GradingAxis) (σ : Fin 3 → Fin 3) (r : RealTrace) (n : ℕ)
                  → GradingAxis                                      -- the ⋊-twisted axis: σ acts on a (the act-φ)
coemit-s4-braided a σ r n = s3-on-axis σ a
