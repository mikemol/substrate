------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2fixesbit0
--
-- Defines: xor2-fixes-bit0
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2fixesbit0 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.Algebra.F2.F2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Parity4periodic
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


xor2-fixes-bit0 : (n : ℕ) → parity (xor2 n) ≡ parity n
xor2-fixes-bit0 zero                        = refl
xor2-fixes-bit0 (suc zero)                  = refl
xor2-fixes-bit0 (suc (suc zero))            = refl
xor2-fixes-bit0 (suc (suc (suc zero)))      = refl
xor2-fixes-bit0 (suc (suc (suc (suc n))))   =
  -- LHS: parity (xor2 (n+4)) = parity ((xor2 n)+4) ≡ parity (xor2 n)   [4-periodic]
  -- RHS: parity (n+4) ≡ parity n                                        [4-periodic]
  trans (parity-4-periodic (xor2 n)) (trans (xor2-fixes-bit0 n) (sym (parity-4-periodic n)))
