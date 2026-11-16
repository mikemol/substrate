------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdigitisv4obj
--
-- Defines: coemit-digit-is-v4-obj
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdigitisv4obj where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipobj
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Digittov4
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2fixesbit0
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2flipsbit1
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


coemit-digit-is-v4-obj : (n : ℕ) → digit-to-v4 (xor2 n) ≡ v4-flip-obj (digit-to-v4 n)
coemit-digit-is-v4-obj n = cong₂ V4.v4 (xor2-fixes-bit0 n) (xor2-flips-bit1 n)
