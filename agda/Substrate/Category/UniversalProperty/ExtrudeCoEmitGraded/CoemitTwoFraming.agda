------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitTwoFraming
--
-- Defines: CoemitTwoFraming
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitTwoFraming where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeupto
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- (2) coemit-native-twoframing: the V₄-symmetric two-framing OF RealTrace directly (not over Fam (Idx D)).
--     μ-frame = the ∂/collapse (trace-mul → z, d²=0, EXACT — the halting/simplicial-boundary side);
--     ν-frame = ~ (bisimilarity, the gfp UP — the non-halting side). The two frames of the one obstruction (328).
record CoemitTwoFraming (a b : RealTrace) : Set where
  field
    μ-collapse : trace-mul a b ~ zero-trace          -- μ: the ∂/square-zero frame (d²=0, EXACT)
    ν-bisim    : ((n : ℕ) → agree-upto n a b) → b ~ a  -- ν: the gfp-UP frame (~, up-to)
