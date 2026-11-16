------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipxor2commute
--
-- Defines: pflip-xor2-commute
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipxor2commute where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


-- XOR-1 and XOR-2 COMMUTE (the abelian F₂² structure on the digit's low two bits).
pflip-xor2-commute : (n : ℕ) → xor2 (pflip n) ≡ pflip (xor2 n)
pflip-xor2-commute zero                       = refl
pflip-xor2-commute (suc zero)                 = refl
pflip-xor2-commute (suc (suc zero))           = refl
pflip-xor2-commute (suc (suc (suc zero)))     = refl
pflip-xor2-commute (suc (suc (suc (suc n))))  = cong (λ k → suc (suc (suc (suc k)))) (pflip-xor2-commute n)
