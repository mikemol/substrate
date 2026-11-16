------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2involutive
--
-- Defines: xor2-involutive
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2involutive where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


xor2-involutive : (n : ℕ) → xor2 (xor2 n) ≡ n
xor2-involutive zero                          = refl
xor2-involutive (suc zero)                    = refl
xor2-involutive (suc (suc zero))              = refl
xor2-involutive (suc (suc (suc zero)))        = refl
xor2-involutive (suc (suc (suc (suc n))))     = cong (λ k → suc (suc (suc (suc k)))) (xor2-involutive n)
