------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone.OrMonotoneRight
--
-- Defines: ∨-monotone-right
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone.OrMonotoneRight where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Or
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq



∨-monotone-right :
  ∀ (a : Bool) {b₁ b₂} →
  (b₁ ≡ true → b₂ ≡ true) →
  (a ∨ b₁) ≡ true → (a ∨ b₂) ≡ true
∨-monotone-right true  _ _   = refl
∨-monotone-right false f hyp = f hyp
