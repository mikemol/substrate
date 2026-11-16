------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbraidissemidirect
--
-- Defines: coemit-braid-is-semidirect
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbraidissemidirect where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3actcomp
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits3braided
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4braided
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4braided
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- THE INVARIANT (the answer to the design question): the braiding is the ⋊ — the V₄ involution (coemit-v4-braided)
-- AND the S₃ permutation (coemit-s3-braided, 339) glued by the twist (s3-on-axis = act φ). Neither alone: the full
-- S₄ = V₄ ⋊ S₃ chain. Witness: the twist s3-on-axis composes as the ⋊ (the semidirect structure, act-hom = s3-act-comp).
coemit-braid-is-semidirect : (a : GradingAxis) (σ τ : Fin 3 → Fin 3)
  → coemit-s4-braided (coemit-s4-braided a τ zero-trace 0) σ zero-trace 0
    ≡ coemit-s4-braided a (λ x → σ (τ x)) zero-trace 0
coemit-braid-is-semidirect a σ τ = s3-act-comp σ τ a
