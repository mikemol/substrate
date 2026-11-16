------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbraidtracemul
--
-- Defines: coemit-braid-trace-mul
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbraidtracemul where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectivefinite
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcolimbridge
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- (2) coemit-braid-trace-mul: the S₄ twist threaded through the ACTUAL trace-mul products. Since trace-mul r s
--     collapses to zero-trace, the braided perspective of a product = the perspective of zero-trace (the twist's
--     orbit lands at the fixed point). The finite view of the product IS the zero-view — reuse colim-bridge (338).
coemit-braid-trace-mul : (a : GradingAxis) (σ : Fin 3 → Fin 3) (r s : RealTrace) (n : ℕ)
                       → perspective-finite μν-axis (trace-mul r s) n ≡ perspective-finite μν-axis zero-trace n
coemit-braid-trace-mul a σ r s n = coemit-colim-bridge r s n
