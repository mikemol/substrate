------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipinvolutive
--
-- Defines: pflip-involutive
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipinvolutive where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


-- pflip IS an involution (unlike the discarded step-flip): pflip² ≡ id, by induction on the 2-step structure.
pflip-involutive : (n : ℕ) → pflip (pflip n) ≡ n
pflip-involutive zero          = refl
pflip-involutive (suc zero)    = refl
pflip-involutive (suc (suc n)) = cong (λ k → suc (suc k)) (pflip-involutive n)
