------------------------------------------------------------------------
-- Substrate.Cocycles.F2CubedPuncturing.PuncturingTransitive
--
-- Defines: puncturing-transitive
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.F2CubedPuncturing; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.F2CubedPuncturing.PuncturingTransitive where

open import Substrate.Foundation.Product
open import Substrate.Groups.F2Cubed
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Cocycles.F2CubedPuncturing.PunctureIndex
open import Substrate.Cocycles.F2CubedPuncturing.PuncturingAct



puncturing-transitive :
  (t₁ t₂ : PunctureIndex) → ∃ λ g → puncturing-act g t₁ ≡ t₂
puncturing-transitive t₁ t₂ = (t₂ + t₁) , proof
  where
    proof : (t₂ + t₁) + t₁ ≡ t₂
    proof = trans (+-assoc t₂ t₁ t₁)
            (cong-trans (t₂ +_) (+-self t₁)
                   (+-identityʳ t₂))
