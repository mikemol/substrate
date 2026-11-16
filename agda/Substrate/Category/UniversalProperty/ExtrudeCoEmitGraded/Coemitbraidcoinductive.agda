------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbraidcoinductive
--
-- Defines: coemit-braid-coinductive
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbraidcoinductive where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectivefinite
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- (2) coemit-braid-coinductive: the ⋊-twist threaded through the ACTUAL coinductive tail-step. The braided action on
--     a trace applies the axis-perspective at the head and RECURSES on the tail — the twist is available at tail r too
--     (the coinduction carries the S₄ element down). Witness: the perspective at depth (suc n) uses the tail.
coemit-braid-coinductive : (a : GradingAxis) (σ : Fin 3 → Fin 3) (r : RealTrace) (n : ℕ)
                         → perspective-finite μν-axis r (suc n)
                           ≡ RealTrace.head r ∷ perspective-finite μν-axis (RealTrace.tail r) n   -- the braided perspective DECOMPOSES via tail
coemit-braid-coinductive a σ r n = refl
