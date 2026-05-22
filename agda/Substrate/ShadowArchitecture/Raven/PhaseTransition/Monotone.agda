------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone
--
-- Monotonicity of historical truth: "once the Raven has spoken, it
-- has always already spoken."
--
--   prior-añelē?-monotone — over arbitrary Vec Stanza n.
--   seen-monotone-raven   — specialised to the 18-stanza Raven.
--
-- Proof structure: induction on Fin indices via the private helper
-- ∨-monotone-right (a ∨ b₁ ≡ true → (b₁ → b₂) → a ∨ b₂ ≡ true).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone where

open import Substrate.Foundation.Bool using (Bool; true; false; _∨_)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ)
open import Substrate.Foundation.Nat using (ℕ) renaming (_≤_ to _ℕ≤_; s≤s to s≤s)
open import Substrate.Foundation.Vec using (Vec; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.ShadowArchitecture.Raven.Grammar using (Stanza)
open import Substrate.ShadowArchitecture.Raven.Poem using (raven)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.IsAñeléTerminal
  using (is-añelē-terminal)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.PriorAñelé
  using (prior-añelē?)

private
  ∨-monotone-right :
    ∀ (a : Bool) {b₁ b₂} →
    (b₁ ≡ true → b₂ ≡ true) →
    (a ∨ b₁) ≡ true → (a ∨ b₂) ≡ true
  ∨-monotone-right true  _ _   = refl
  ∨-monotone-right false f hyp = f hyp

prior-añelē?-monotone :
  ∀ {n} (v : Vec Stanza n) (i j : Fin n) →
  (toℕ i ℕ≤ toℕ j) →
  prior-añelē? v i ≡ true →
  prior-añelē? v j ≡ true
prior-añelē?-monotone (s ∷ ss) zero    zero    _       ()
prior-añelē?-monotone (s ∷ ss) zero    (suc j) _       ()
prior-añelē?-monotone (s ∷ ss) (suc i) (suc j) (s≤s p) hyp =
  ∨-monotone-right (is-añelē-terminal s)
    (prior-añelē?-monotone ss i j p)
    hyp

seen-monotone-raven :
  ∀ (i j : Fin 18) →
  (toℕ i ℕ≤ toℕ j) →
  prior-añelē? raven i ≡ true →
  prior-añelē? raven j ≡ true
seen-monotone-raven = prior-añelē?-monotone raven
